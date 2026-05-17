"""Typed result models for parsed simulation outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np

ArrayLike = np.ndarray

__all__ = [
    "BandStructure",
    "DensityOfStates",
    "ElectronicStep",
    "ElectronicSteps",
    "IonicStep",
    "IonicSteps",
    "ProjectedDensityOfStates",
]


@dataclass(frozen=True, slots=True)
class ElectronicStep:
    """One electronic self-consistency iteration."""

    ionic_step: int
    step: int
    algorithm: str
    energy: float | None = None
    energy_change: float | None = None
    epsilon_change: float | None = None
    ncg: int | None = None
    rms: float | None = None
    rms_c: float | None = None
    values: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ElectronicStep":
        return cls(
            ionic_step=int(data.get("ionic_step", 0)),
            step=int(data.get("electronic_step", data.get("step", 0))),
            algorithm=str(data.get("algorithm", "")),
            energy=_optional_float(data.get("energy")),
            energy_change=_optional_float(data.get("dE", data.get("energy_change"))),
            epsilon_change=_optional_float(data.get("d_eps", data.get("epsilon_change"))),
            ncg=_optional_int(data.get("ncg")),
            rms=_optional_float(data.get("rms")),
            rms_c=_optional_float(data.get("rms_c")),
            values=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        row = {
            "ionic_step": self.ionic_step,
            "electronic_step": self.step,
            "algorithm": self.algorithm,
            "energy": self.energy,
            "dE": self.energy_change,
            "d_eps": self.epsilon_change,
            "ncg": self.ncg,
            "rms": self.rms,
            "rms_c": self.rms_c,
        }
        row.update({key: value for key, value in self.values.items() if key not in row})
        return {key: value for key, value in row.items() if value is not None}


@dataclass(frozen=True, slots=True)
class ElectronicSteps(Sequence[ElectronicStep]):
    """Electronic convergence history with convenient table helpers."""

    steps: tuple[ElectronicStep, ...] | Iterable[ElectronicStep] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self) -> Iterator[ElectronicStep]:
        return iter(self.steps)

    def __getitem__(self, index):
        return self.steps[index]

    def by_ionic_step(self, ionic_step: int) -> tuple[ElectronicStep, ...]:
        return tuple(step for step in self.steps if step.ionic_step == ionic_step)

    def final_per_ionic_step(self) -> tuple[ElectronicStep, ...]:
        latest: dict[int, ElectronicStep] = {}
        for step in self.steps:
            latest[step.ionic_step] = step
        return tuple(latest[key] for key in sorted(latest))

    def to_rows(self) -> list[dict[str, Any]]:
        return [step.to_dict() for step in self.steps]

    def to_dataframe(self):
        import pandas as pd

        return pd.DataFrame(self.to_rows())


@dataclass(frozen=True, slots=True)
class IonicStep:
    """One ionic optimization or molecular-dynamics step."""

    step: int
    ionic_step: int | None = None
    free_energy: float | None = None
    zero_energy: float | None = None
    energy_change: float | None = None
    temperature: float | None = None
    kinetic_energy: float | None = None
    predictor_corrector: float | None = None
    nose_kinetic_energy: float | None = None
    magnetization: float | None = None
    values: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "IonicStep":
        step = int(data.get("step", data.get("ionic_step", 0)))
        return cls(
            step=step,
            ionic_step=_optional_int(data.get("ionic_step")) or step,
            free_energy=_optional_float(data.get("F")),
            zero_energy=_optional_float(data.get("E0")),
            energy_change=_optional_float(data.get("dE", data.get("d E"))),
            temperature=_optional_float(data.get("T")),
            kinetic_energy=_optional_float(data.get("EK")),
            predictor_corrector=_optional_float(data.get("SP")),
            nose_kinetic_energy=_optional_float(data.get("SK")),
            magnetization=_optional_float(data.get("mag")),
            values=dict(data),
        )

    def to_dict(self) -> dict[str, Any]:
        row = {
            "ionic_step": self.ionic_step,
            "step": self.step,
            "F": self.free_energy,
            "E0": self.zero_energy,
            "dE": self.energy_change,
            "T": self.temperature,
            "EK": self.kinetic_energy,
            "SP": self.predictor_corrector,
            "SK": self.nose_kinetic_energy,
            "mag": self.magnetization,
        }
        row.update({key: value for key, value in self.values.items() if key not in row})
        return {key: value for key, value in row.items() if value is not None}


@dataclass(frozen=True, slots=True)
class IonicSteps(Sequence[IonicStep]):
    """Ionic convergence or MD history."""

    steps: tuple[IonicStep, ...] | Iterable[IonicStep] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self) -> Iterator[IonicStep]:
        return iter(self.steps)

    def __getitem__(self, index):
        return self.steps[index]

    def to_rows(self) -> list[dict[str, Any]]:
        return [step.to_dict() for step in self.steps]

    def to_dataframe(self):
        import pandas as pd

        return pd.DataFrame(self.to_rows())


@dataclass(frozen=True, slots=True)
class ProjectedDensityOfStates:
    """Projected DOS block for one atom or projection group."""

    atom_index: int
    data: ArrayLike
    header: ArrayLike | None = None
    labels: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", np.asarray(self.data, dtype=np.float64))
        if self.header is not None:
            object.__setattr__(self, "header", np.asarray(self.header, dtype=np.float64))
        object.__setattr__(self, "labels", tuple(self.labels))

    def to_dataframe(self):
        import pandas as pd

        columns = _dos_columns(self.data.shape[1], self.labels)
        dataframe = pd.DataFrame(self.data, columns=columns)
        dataframe.insert(0, "atom_index", self.atom_index)
        return dataframe


@dataclass(frozen=True, slots=True)
class DensityOfStates:
    """Total and projected density of states from DOSCAR-like files."""

    atom_count: int
    energy_min: float
    energy_max: float
    fermi_energy: float
    total: ArrayLike
    projected: tuple[ProjectedDensityOfStates, ...] | Iterable[ProjectedDensityOfStates] = field(
        default_factory=tuple
    )
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "total", np.asarray(self.total, dtype=np.float64))
        object.__setattr__(self, "projected", tuple(self.projected))
        object.__setattr__(self, "properties", dict(self.properties))

    @property
    def nedos(self) -> int:
        return int(self.total.shape[0])

    @property
    def energies(self) -> ArrayLike:
        return self.total[:, 0]

    @property
    def shifted_energies(self) -> ArrayLike:
        return self.energies - self.fermi_energy

    def to_dataframe(self, *, shifted: bool = False):
        import pandas as pd

        columns = _dos_columns(self.total.shape[1], ())
        dataframe = pd.DataFrame(self.total, columns=columns)
        if shifted:
            dataframe.insert(1, "energy_minus_fermi", self.shifted_energies)
        return dataframe


@dataclass(frozen=True, slots=True)
class BandStructure:
    """K-point band energies and occupations from EIGENVAL-like files."""

    electron_count: int
    kpoints: ArrayLike
    weights: ArrayLike
    bands: ArrayLike
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "kpoints", np.asarray(self.kpoints, dtype=np.float64))
        object.__setattr__(self, "weights", np.asarray(self.weights, dtype=np.float64))
        object.__setattr__(self, "bands", np.asarray(self.bands, dtype=np.float64))
        object.__setattr__(self, "properties", dict(self.properties))

    @property
    def kpoint_count(self) -> int:
        return int(self.kpoints.shape[0])

    @property
    def band_count(self) -> int:
        return int(self.bands.shape[1]) if self.bands.ndim >= 2 else 0

    def to_dataframe(self):
        import pandas as pd

        rows = []
        value_columns = _band_value_columns(self.bands.shape[2] if self.bands.ndim == 3 else 0)
        for kpoint_index in range(self.kpoint_count):
            kx, ky, kz = self.kpoints[kpoint_index]
            weight = self.weights[kpoint_index]
            for band_index in range(self.band_count):
                row = {
                    "kpoint_index": kpoint_index,
                    "band_index": band_index,
                    "kx": kx,
                    "ky": ky,
                    "kz": kz,
                    "weight": weight,
                }
                row.update(
                    {
                        column: self.bands[kpoint_index, band_index, value_index]
                        for value_index, column in enumerate(value_columns)
                    }
                )
                rows.append(row)
        return pd.DataFrame(rows)


def _dos_columns(count: int, labels: Sequence[str]) -> list[str]:
    if labels and len(labels) == count:
        return list(labels)
    if count == 5:
        return ["energy", "dos_up", "dos_down", "integrated_dos_up", "integrated_dos_down"]
    defaults = ["energy", "dos", "integrated_dos"]
    if count <= len(defaults):
        return defaults[:count]
    return defaults + [f"value_{index}" for index in range(len(defaults), count)]


def _band_value_columns(count: int) -> list[str]:
    if count == 2:
        return ["energy", "occupation"]
    if count == 4:
        return ["energy_up", "energy_down", "occupation_up", "occupation_down"]
    return [f"value_{index + 1}" for index in range(count)]


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)
