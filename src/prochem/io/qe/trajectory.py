"""Quantum ESPRESSO parsers returning unified ProChem calculation models."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

import logging
import re
import traceback
from pathlib import Path

import numpy as np

from prochem.core.models import Calculation, Cell, Trajectory
from prochem.io.base import AbstractParser

logger = logging.getLogger(__name__)

__all__ = ["Parser"]

BOHR_PER_ANGSTROM = 1.889725988579
ATOMIC_TIME_TO_FS = 0.024189
_ASSIGN_RE = re.compile(r"\b(?P<key>nat|ntyp)\s*=\s*(?P<value>\d+)", re.IGNORECASE)


class Parser(AbstractParser):
    """Parser for simple Quantum ESPRESSO MD output folders."""

    engine = "quantum_espresso"

    @classmethod
    def can_parse(cls, path: str | Path) -> bool:
        """Return True for QE input/output folders or known QE sidecar files."""
        file_path = Path(path)
        root = file_path if file_path.is_dir() else file_path.parent
        return _find_qe_files(root) is not None

    def parse(self) -> Calculation:
        """Parse the configured QE folder or file."""
        try:
            root = self.source if self.source.is_dir() else self.source.parent
            files = _find_qe_files(root)
            if files is None:
                return self._error_calculation("No Quantum ESPRESSO .in/.pos/.cel file set was found.")

            input_info = _read_input_file(files["input"])
            cell_vectors = _read_cell_file(files["cell"])
            positions, time_fs, timestep_fs = _read_position_file(files["positions"])
            positions = positions / BOHR_PER_ANGSTROM
            direct_positions = positions @ np.linalg.inv(cell_vectors)

            species = input_info["species"]
            if species.shape[0] != positions.shape[1]:
                return self._error_calculation(
                    "QE input atom count does not match trajectory position count."
                )

            trajectory = Trajectory.from_arrays(
                species=species,
                positions=positions,
                direct_positions=direct_positions,
                cell=Cell(cell_vectors),
                time_fs=time_fs,
                timestep_fs=timestep_fs,
                masses=input_info["masses"],
                properties={
                    "format": "qe-md",
                    "input_file": str(files["input"]),
                    "positions_file": str(files["positions"]),
                    "cell_file": str(files["cell"]),
                },
            )
            return Calculation(
                source=self.source,
                engine=self.engine,
                trajectory=trajectory,
                properties={"file_type": "qe-md"},
            )
        except Exception:
            logger.exception("QE parsing failed for %s", self.source)
            return self._error_calculation(traceback.format_exc())


def _find_qe_files(root: Path) -> dict[str, Path] | None:
    if not root.exists():
        return None

    for directory in [root, *[path for path in root.rglob("*") if path.is_dir()]]:
        files = {path.suffix.lower().lstrip("."): path for path in directory.iterdir() if path.is_file()}
        input_file = next((path for path in directory.iterdir() if path.suffix.lower() == ".in"), None)
        if input_file and "pos" in files and "cel" in files:
            return {
                "input": input_file,
                "positions": files["pos"],
                "cell": files["cel"],
            }
    return None


def _read_input_file(path: Path) -> dict[str, np.ndarray]:
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    atom_count = None
    type_count = None
    masses_by_symbol: dict[str, float] = {}
    species: list[str] = []
    masses: list[float] = []

    for index, line in enumerate(text):
        for match in _ASSIGN_RE.finditer(line):
            if match.group("key").lower() == "nat":
                atom_count = int(match.group("value"))
            elif match.group("key").lower() == "ntyp":
                type_count = int(match.group("value"))

        stripped = line.strip().upper()
        if stripped.startswith("ATOMIC_SPECIES") and type_count is not None:
            for offset in range(1, type_count + 1):
                symbol, mass, *_ = text[index + offset].split()
                masses_by_symbol[symbol] = _float_from_fortran(mass)

        elif stripped.startswith("ATOMIC_POSITIONS") and atom_count is not None:
            for offset in range(1, atom_count + 1):
                symbol = text[index + offset].split()[0]
                species.append(symbol)
                masses.append(masses_by_symbol.get(symbol, np.nan))

    if atom_count is None:
        raise ValueError(f"No nat value was found in {path}.")
    if len(species) != atom_count:
        raise ValueError(f"No complete ATOMIC_POSITIONS block was found in {path}.")

    return {
        "species": np.asarray(species, dtype=str),
        "masses": np.asarray(masses, dtype=np.float64),
    }


def _read_cell_file(path: Path) -> np.ndarray:
    lines = [line.split() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    vectors = []
    for tokens in lines:
        if len(tokens) >= 3:
            try:
                vectors.append([_float_from_fortran(token) for token in tokens[:3]])
            except ValueError:
                continue
        if len(vectors) == 3:
            break
    if len(vectors) != 3:
        raise ValueError(f"No complete cell was found in {path}.")
    return np.asarray(vectors, dtype=np.float64) / BOHR_PER_ANGSTROM


def _read_position_file(path: Path) -> tuple[np.ndarray, np.ndarray | None, float | None]:
    frames: list[list[list[float]]] = []
    times_au: list[float] = []
    current: list[list[float]] = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        tokens = line.split()
        if not tokens:
            continue
        if len(tokens) == 2:
            if current:
                frames.append(current)
                current = []
            times_au.append(_float_from_fortran(tokens[-1]))
        elif len(tokens) >= 3:
            current.append([_float_from_fortran(token) for token in tokens[:3]])

    if current:
        frames.append(current)
    if not frames:
        raise ValueError(f"No position frames were found in {path}.")

    positions = np.asarray(frames, dtype=np.float64)
    if times_au:
        time_fs = np.asarray(times_au[: positions.shape[0]], dtype=np.float64) * ATOMIC_TIME_TO_FS
        timestep_fs = float(np.median(np.diff(time_fs))) if time_fs.size > 1 else None
    else:
        time_fs = None
        timestep_fs = None
    return positions, time_fs, timestep_fs


def _float_from_fortran(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e").rstrip(","))
