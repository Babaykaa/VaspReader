"""Structure-sequence assembly utilities."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Literal, Optional, Sequence

import numpy as np

from prochem.core.models import Atom, Calculation, Structure, Structures
from prochem.core.structures import Timestep

MergeStatus = Literal[
    "first",
    "exact_overlap",
    "deletion_overlap",
    "mismatch",
]


@dataclass(frozen=True, slots=True)
class StructuresMergePolicy:
    """Policy for joining restarted structure sequences."""

    direct_tolerance: float = 1e-4
    cartesian_tolerance: float = 1e-3
    drop_exact_overlap: bool = True
    keep_topology_change_frame: bool = True
    allow_deletions: bool = True
    allow_mismatch_fallback: bool = True
    boundary_search_frames: int = 6


@dataclass(frozen=True, slots=True)
class MergeEvent:
    """One boundary decision made while merging structure sequences."""

    status: MergeStatus
    previous_source: Optional[Path]
    next_source: Path
    previous_step_count: int
    next_step_count: int
    previous_atom_count: int
    next_atom_count: int
    dropped_next_frames: int = 0
    deleted_atom_ids: tuple[int, ...] = ()
    matched_next_frame: int = 0
    max_delta: Optional[float] = None
    message: str = ""


@dataclass(frozen=True, slots=True)
class MergeReport:
    """Summary of a structure-sequence merge."""

    events: tuple[MergeEvent, ...]
    source_files: tuple[Path, ...]
    total_frames: int
    total_atoms: int
    deleted_atom_ids: tuple[int, ...] = ()
    segment_timestep: tuple[Timestep, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def has_mismatches(self) -> bool:
        """Whether any boundary could not be matched."""
        return any(event.status == "mismatch" for event in self.events)


@dataclass(slots=True)
class StructuresAssembler:
    """Merge calculations produced by structure-sequence parsers."""

    policy: StructuresMergePolicy = field(default_factory=StructuresMergePolicy)

    def merge_calculations(self, calculations: Sequence[Calculation]) -> tuple[Calculation, MergeReport]:
        """Merge calculations into one calculation and return a report."""
        prepared = [calculation for calculation in calculations if calculation.structures is not None]
        if not prepared:
            raise ValueError("At least one calculation with structures is required.")

        registry = _registry_from_structures(prepared[0].structures)
        frames = [
            _copy_frame_with_ids(
                frame,
                frame.atom_ids,
                source=prepared[0].structures.sources[index],
                source_step=index,
            )
            for index, frame in enumerate(prepared[0].structures.frames)
        ]
        frame_sources = list(prepared[0].structures.sources)
        source_files = [prepared[0].source]
        events = [
            MergeEvent(
                status="first",
                previous_source=None,
                next_source=prepared[0].source,
                previous_step_count=0,
                next_step_count=prepared[0].step_count,
                previous_atom_count=0,
                next_atom_count=prepared[0].atom_count,
                message="Initial structures segment.",
            )
        ]
        deleted_atom_ids: set[int] = set()
        segment_timestep: list[tuple[int, Timestep]] = [(0, prepared[0].structures.timestep)]
        warnings = _merge_warnings([structures.timestep for structures in _structures(prepared)])

        for calculation in prepared[1:]:
            source_files.append(calculation.source)
            next_structures = calculation.structures
            previous_frame = frames[-1]
            decision = self._decide_boundary(previous_frame, next_structures)
            next_first = next_structures.frame(decision.matched_next_frame)

            if decision.status == "mismatch" and not self.policy.allow_mismatch_fallback:
                raise ValueError(decision.message)

            if decision.status == "mismatch":
                mapping, registry = _register_new_atoms(next_first, registry)
                start_index = 0
            else:
                mapping = decision.next_to_previous_atom_ids
                start_index = decision.dropped_next_frames

            deleted_atom_ids.update(decision.deleted_atom_ids)
            events.append(
                MergeEvent(
                    status=decision.status,
                    previous_source=source_files[-2],
                    next_source=calculation.source,
                    previous_step_count=len(frames),
                    next_step_count=next_structures.step_count,
                    previous_atom_count=previous_frame.atom_count,
                    next_atom_count=next_first.atom_count,
                    dropped_next_frames=decision.dropped_next_frames,
                    deleted_atom_ids=tuple(decision.deleted_atom_ids),
                    matched_next_frame=decision.matched_next_frame,
                    max_delta=decision.max_delta,
                    message=decision.message,
                )
            )

            time_offset = _time_offset(previous_frame, next_first)
            segment_start = len(frames)
            segment_timestep.append((segment_start, next_structures.timestep))
            for local_step, frame in enumerate(next_structures.frames[start_index:], start=start_index):
                frames.append(
                    _copy_frame_with_ids(
                        frame,
                        [mapping[int(atom_id)] for atom_id in frame.atom_ids],
                        source=next_structures.sources[local_step] or calculation.source,
                        source_step=local_step,
                        time_offset=time_offset,
                    )
                )
                frame_sources.append(next_structures.sources[local_step] or calculation.source)

        structures = Structures(
            frames=frames,
            timestep=_merged_timestep(segment_timestep),
            sources=frame_sources,
            properties={
                "merged": True,
                "source_files": tuple(source_files),
                "segment_timestep": tuple(value for _, value in segment_timestep),
                "policy": self.policy,
            },
        )
        calculation = Calculation(
            source=source_files[-1].parent,
            engine=prepared[0].engine,
            structures=structures,
            properties={
                "merged": True,
                "source_files": tuple(source_files),
                "segment_timestep": tuple(value for _, value in segment_timestep),
            },
            warnings=warnings,
        )
        report = MergeReport(
            events=tuple(events),
            source_files=tuple(source_files),
            total_frames=structures.step_count,
            total_atoms=structures.atom_count,
            deleted_atom_ids=tuple(sorted(deleted_atom_ids)),
            segment_timestep=tuple(value for _, value in segment_timestep),
            warnings=tuple(warnings),
        )
        return calculation, report

    def _decide_boundary(self, previous: Structure, next_structures: Structures) -> "_BoundaryDecision":
        search_count = max(1, min(self.policy.boundary_search_frames, next_structures.step_count))
        for next_frame_index in range(search_count):
            next_frame = next_structures.frame(next_frame_index)
            if _same_species(previous.species, next_frame.species):
                max_delta = _frame_max_delta(previous, next_frame)
                if max_delta is not None and max_delta <= self._active_tolerance(previous, next_frame):
                    dropped = next_frame_index + 1 if self.policy.drop_exact_overlap else next_frame_index
                    return _BoundaryDecision(
                        status="exact_overlap",
                        next_to_previous_atom_ids={
                            int(atom_id): int(previous.atom_ids[index])
                            for index, atom_id in enumerate(next_frame.atom_ids)
                        },
                        dropped_next_frames=dropped,
                        matched_next_frame=next_frame_index,
                        max_delta=max_delta,
                        message="Boundary frames are identical within tolerance.",
                    )

            if self.policy.allow_deletions and next_frame.atom_count <= previous.atom_count:
                match = _ordered_subset_match(
                    previous,
                    next_frame,
                    tolerance=self._active_tolerance(previous, next_frame),
                )
                if match is not None:
                    mapping, deleted_atom_ids, max_delta = match
                    dropped = next_frame_index if self.policy.keep_topology_change_frame else next_frame_index + 1
                    return _BoundaryDecision(
                        status="deletion_overlap",
                        next_to_previous_atom_ids=mapping,
                        dropped_next_frames=dropped,
                        matched_next_frame=next_frame_index,
                        deleted_atom_ids=tuple(sorted(deleted_atom_ids)),
                        max_delta=max_delta,
                        message="Next segment matches a subset of the previous segment.",
                    )

        return _BoundaryDecision(
            status="mismatch",
            next_to_previous_atom_ids={},
            message=f"Boundary frames could not be matched in the first {search_count} next frames.",
        )

    def _active_tolerance(self, previous: Structure, next_first: Structure) -> float:
        if previous.direct_positions is not None and next_first.direct_positions is not None:
            return self.policy.direct_tolerance
        return self.policy.cartesian_tolerance


@dataclass(frozen=True, slots=True)
class _BoundaryDecision:
    status: MergeStatus
    next_to_previous_atom_ids: dict[int, int]
    dropped_next_frames: int = 0
    deleted_atom_ids: tuple[int, ...] = ()
    matched_next_frame: int = 0
    max_delta: Optional[float] = None
    message: str = ""


def merge_calculations(
    calculations: Sequence[Calculation],
    policy: Optional[StructuresMergePolicy] = None,
) -> tuple[Calculation, MergeReport]:
    """Merge calculations using the provided policy."""
    return StructuresAssembler(policy or StructuresMergePolicy()).merge_calculations(calculations)


def _structures(calculations: Sequence[Calculation]) -> tuple[Structures, ...]:
    return tuple(calculation.structures for calculation in calculations if calculation.structures is not None)


def _registry_from_structures(structures: Structures) -> list[Atom]:
    return [structures.atom_record(atom_id).copy() for atom_id in structures.atom_ids]


def _register_new_atoms(frame: Structure, registry: list[Atom]) -> tuple[dict[int, int], list[Atom]]:
    next_id = max((record.atom_id for record in registry), default=-1) + 1
    mapping = {}
    for local_index, atom_id in enumerate(frame.atom_ids):
        new_id = next_id
        next_id += 1
        mapping[int(atom_id)] = new_id
        mass = None if frame.masses is None else float(frame.masses[local_index])
        registry.append(
            Atom(
                atom_id=new_id,
                species=str(frame.species[local_index]),
                initial_index=len(registry),
                mass=mass,
                properties={"created_by": "mismatch_merge"},
            )
        )
    return mapping, registry


def _copy_frame_with_ids(
    frame: Structure,
    atom_ids: Iterable[int],
    *,
    source: Optional[Path] = None,
    source_step: Optional[int] = None,
    time_offset: Optional[float] = None,
) -> Structure:
    properties = dict(frame.properties)
    if source is not None:
        properties["source"] = source
    if source_step is not None:
        properties["source_step"] = source_step
    time_fs = frame.time_fs
    if time_fs is not None and time_offset is not None:
        time_fs = time_fs + time_offset
    return Structure(
        species=frame.species,
        positions=frame.positions,
        atom_ids=np.asarray(list(atom_ids), dtype=np.int64),
        cell=frame.cell,
        direct_positions=frame.direct_positions,
        masses=frame.masses,
        velocities=frame.velocities,
        forces=frame.forces,
        atom_potential_energies=frame.atom_potential_energies_array(),
        atom_kinetic_energies=frame.atom_kinetic_energies_array(),
        atom_total_energies=frame.atom_total_energies_array(),
        stress=frame.stress,
        potential_energy=frame.potential_energy,
        kinetic_energy=frame.kinetic_energy,
        total_energy=frame.total_energy,
        time_fs=time_fs,
        properties=properties,
    )


def _same_species(left: np.ndarray, right: np.ndarray) -> bool:
    return left.shape == right.shape and np.array_equal(left, right)


def _frame_max_delta(left: Structure, right: Structure) -> Optional[float]:
    if left.atom_count != right.atom_count:
        return None
    if left.direct_positions is not None and right.direct_positions is not None:
        return float(np.max(np.abs(_pbc_delta(left.direct_positions, right.direct_positions))))
    return float(np.max(np.abs(left.positions - right.positions)))


def _ordered_subset_match(
    previous: Structure,
    next_first: Structure,
    tolerance: float,
) -> Optional[tuple[dict[int, int], set[int], float]]:
    mapping: dict[int, int] = {}
    matched_previous_ids: set[int] = set()
    max_delta = 0.0
    start = 0
    for next_index, (next_species, next_atom_id) in enumerate(
        zip(next_first.species, next_first.atom_ids, strict=True)
    ):
        found_index = None
        found_delta = None
        for previous_index in range(start, previous.atom_count):
            if previous.atom_ids[previous_index] in matched_previous_ids:
                continue
            if previous.species[previous_index] != next_species:
                continue
            delta = _atom_delta(previous, previous_index, next_first, next_index)
            if delta <= tolerance:
                found_index = previous_index
                found_delta = delta
                break
        if found_index is None:
            return None
        previous_atom_id = int(previous.atom_ids[found_index])
        mapping[int(next_atom_id)] = previous_atom_id
        matched_previous_ids.add(previous_atom_id)
        max_delta = max(max_delta, float(found_delta))
        start = found_index + 1
    deleted_atom_ids = set(int(atom_id) for atom_id in previous.atom_ids) - matched_previous_ids
    return mapping, deleted_atom_ids, max_delta


def _atom_delta(left: Structure, left_index: int, right: Structure, right_index: int) -> float:
    if left.direct_positions is not None and right.direct_positions is not None:
        delta = _pbc_delta(left.direct_positions[left_index], right.direct_positions[right_index])
    else:
        delta = left.positions[left_index] - right.positions[right_index]
    return float(np.max(np.abs(delta)))


def _pbc_delta(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    delta = np.asarray(left, dtype=np.float64) - np.asarray(right, dtype=np.float64)
    return delta - np.round(delta)


def _time_offset(previous: Structure, next_first: Structure) -> Optional[float]:
    if previous.time_fs is None or next_first.time_fs is None:
        return None
    return previous.time_fs - next_first.time_fs


def _merged_timestep(segments: Sequence[tuple[int, Timestep]]) -> Timestep:
    known = [(start, value) for start, value in segments if value is not None]
    if not known:
        return None
    if any(isinstance(value, dict) for _, value in known):
        merged: dict[int, float] = {}
        for start, value in known:
            if isinstance(value, dict):
                merged.update({start + int(step): float(step_value) for step, step_value in value.items()})
            else:
                merged[start] = float(value)
        return dict(sorted(merged.items()))

    first = float(known[0][1])
    if all(np.isclose(float(value), first, rtol=0.0, atol=1e-12) for _, value in known[1:]):
        return first
    return {start: float(value) for start, value in known}


def _merge_warnings(timesteps: Sequence[Timestep]) -> list[str]:
    warnings = []
    known = [value for value in timesteps if value is not None]
    if len(known) != len(timesteps):
        warnings.append("Some structure segments do not define timestep.")
    if len({repr(value) for value in known}) > 1:
        warnings.append("Merged structures contain segments with different timestep values.")
    return warnings
