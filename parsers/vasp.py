"""VASP parsers returning unified ProChem calculation models."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

import logging
import re
import traceback
from enum import Enum
from pathlib import Path

import numpy as np

from core.models import Calculation, Cell, Trajectory
from core.trajectory import MergeReport, TrajectoryMergePolicy, merge_calculations
from parsers.parser import AbstractParser

logger = logging.getLogger(__name__)

__all__ = [
    "Parser",
    "VASPfileType",
    "discover_vasprun_files",
    "parse_vasprun_sequence",
]

_TAG_VALUE_RE = re.compile(r"<c[^>]*>\s*([^<]+?)\s*</c>")
_FLOAT_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?")


class VASPfileType(Enum):
    """Supported VASP file types."""

    XML = "vasprun.xml"
    OUTCAR = "OUTCAR"
    XDATCAR = "XDATCAR"
    POSCAR = "POSCAR"
    CONTCAR = "CONTCAR"
    CHGCAR = "CHGCAR"
    CHG = "CHG"
    OSZICAR = "OSZICAR"
    DOSCAR = "DOSCAR"
    EIGENVAL = "EIGENVAL"
    UNKNOWN = "UNKNOWN"


class Parser(AbstractParser):
    """Parser for VASP structure and trajectory files."""

    engine = "vasp"

    def __init__(self, source: str | Path) -> None:
        super().__init__(source)
        self.__file_type = self.define_file_type(self.source)

    @classmethod
    def can_parse(cls, path: str | Path) -> bool:
        """Return True for common VASP files."""
        source = Path(path)
        if source.is_dir():
            return bool(discover_vasprun_files(source, recursive=True))
        return cls.define_file_type(path) is not VASPfileType.UNKNOWN

    @staticmethod
    def define_file_type(path: str | Path) -> VASPfileType:
        """Define VASP file type from the basename."""
        file_path = Path(path)
        name = file_path.name.upper()
        suffix = file_path.suffix.lower()
        if suffix == ".xml" or name == "VASPRUN.XML":
            return VASPfileType.XML
        if name.startswith("OUTCAR"):
            return VASPfileType.OUTCAR
        if name.startswith("XDATCAR"):
            return VASPfileType.XDATCAR
        if name.startswith("POSCAR"):
            return VASPfileType.POSCAR
        if name.startswith("CONTCAR"):
            return VASPfileType.CONTCAR
        if name.startswith("CHGCAR"):
            return VASPfileType.CHGCAR
        if name.startswith("CHG"):
            return VASPfileType.CHG
        if name.startswith("OSZICAR"):
            return VASPfileType.OSZICAR
        if name.startswith("DOSCAR"):
            return VASPfileType.DOSCAR
        if name.startswith("EIGENVAL"):
            return VASPfileType.EIGENVAL
        return VASPfileType.UNKNOWN

    def parse(self) -> Calculation:
        """Parse the configured VASP input."""
        try:
            if self.source.is_dir():
                calculation, report = parse_vasprun_sequence(self.source, recursive=True)
                calculation.properties["merge_report"] = report
                return calculation
            match self.__file_type:
                case VASPfileType.XML:
                    return self.read_vasprun()
                case VASPfileType.OUTCAR:
                    return self.read_outcar()
                case VASPfileType.XDATCAR:
                    return self.read_xdatcar()
                case VASPfileType.POSCAR | VASPfileType.CONTCAR:
                    return self.read_poscar()
                case VASPfileType.CHG | VASPfileType.CHGCAR:
                    return self.read_chgcar()
                case VASPfileType.OSZICAR:
                    return self.read_oszicar()
                case VASPfileType.DOSCAR:
                    return self.read_doscar()
                case VASPfileType.EIGENVAL:
                    return self.read_eigenval()
                case VASPfileType.UNKNOWN:
                    return self._error_calculation("Unknown VASP file type.")
        except Exception:
            logger.exception("VASP parsing failed for %s", self.source)
            return self._error_calculation(traceback.format_exc())

    def read_vasprun(self) -> Calculation:
        """Read a VASP vasprun.xml file."""
        atom_count = 0
        atom_types: list[int] = []
        species: list[str] = []
        pomass_by_type: list[float] = []
        position_frames: list[list[list[float]]] = []
        force_frames: list[list[list[float]]] = []
        cell_frames: list[list[list[float]]] = []
        initial_cell: list[list[float]] | None = None
        timestep_fs: float | None = None
        in_calculation = False

        with self.source.open("r", encoding="utf-8", errors="replace") as xml:
            while True:
                line = xml.readline()
                if not line:
                    break

                if "<calculation>" in line:
                    in_calculation = True
                elif "</calculation>" in line:
                    in_calculation = False

                if "<atoms>" in line:
                    numbers = _numbers_from_line(line)
                    if numbers:
                        atom_count = int(numbers[0])

                elif 'name="POMASS"' in line:
                    pomass_by_type = _numbers_from_line(line)

                elif 'name="POTIM"' in line and timestep_fs is None:
                    values = _numbers_from_line(line)
                    if values:
                        timestep_fs = float(values[-1])

                elif '<field type="int">atomtype</field>' in line:
                    species, atom_types = self._read_atominfo_rows(xml, atom_count)

                elif '<varray name="basis"' in line:
                    basis = _read_vasp_varray(xml, 3)
                    if in_calculation:
                        cell_frames.append(basis)
                    elif initial_cell is None:
                        initial_cell = basis

                elif '<varray name="positions"' in line and in_calculation:
                    position_frames.append(_read_vasp_varray(xml, atom_count))

                elif '<varray name="forces"' in line and in_calculation:
                    force_frames.append(_read_vasp_varray(xml, atom_count))

        if not species:
            return self._error_calculation("No atom information was found in vasprun.xml.")
        if not position_frames:
            return self._error_calculation("No trajectory positions were found in vasprun.xml.")

        cell_vectors = np.asarray(
            cell_frames[0] if cell_frames else initial_cell,
            dtype=np.float64,
        )
        if cell_vectors.shape != (3, 3):
            return self._error_calculation("No valid cell basis was found in vasprun.xml.")

        direct_positions = np.asarray(position_frames, dtype=np.float64)
        cells = (
            np.asarray(cell_frames, dtype=np.float64)
            if len(cell_frames) == len(position_frames)
            else cell_vectors
        )
        positions = (
            np.einsum("sai,sij->saj", direct_positions, cells)
            if isinstance(cells, np.ndarray) and cells.ndim == 3
            else direct_positions @ cell_vectors
        )
        forces = np.asarray(force_frames, dtype=np.float64) if force_frames else None
        masses = _masses_from_atom_types(atom_types, pomass_by_type)
        time_fs = (
            np.arange(len(position_frames), dtype=np.float64) * timestep_fs
            if timestep_fs is not None
            else None
        )

        trajectory = Trajectory.from_arrays(
            species=np.asarray(species, dtype=str),
            positions=positions,
            direct_positions=direct_positions,
            cell=cells,
            time_fs=time_fs,
            timestep_fs=timestep_fs,
            masses=masses,
            forces=forces,
            properties={
                "format": "vasprun.xml",
                "cell_frames": cells if isinstance(cells, np.ndarray) and cells.ndim == 3 else None,
            },
        )
        return Calculation(
            source=self.source,
            engine=self.engine,
            trajectory=trajectory,
            properties={"file_type": self.__file_type.value},
        )

    def read_poscar(self) -> Calculation:
        """Read POSCAR/CONTCAR structure files."""
        lines = _read_nonempty_lines(self.source)
        try:
            parsed = _parse_poscar_lines(lines)
        except ValueError as error:
            return self._error_calculation(str(error))
        trajectory = Trajectory.from_arrays(
            species=parsed["species"],
            positions=parsed["positions"],
            direct_positions=parsed["direct_positions"],
            cell=Cell(parsed["cell"]),
        )
        return Calculation(
            source=self.source,
            engine=self.engine,
            trajectory=trajectory,
            properties={
                "file_type": self.__file_type.value,
                "comment": parsed["comment"],
                "symbols": parsed["symbols"],
                "counts": parsed["counts"],
                "selective_dynamics": parsed["selective_dynamics"],
            },
        )

    def read_xdatcar(self) -> Calculation:
        """Read VASP XDATCAR trajectory files."""
        lines = _read_nonempty_lines(self.source)
        try:
            header = _parse_xdatcar_header(lines)
        except ValueError as error:
            return self._error_calculation(str(error))

        frames = []
        configuration_indices = []
        cursor = header["positions_start"]
        atom_count = int(sum(header["counts"]))
        while cursor < len(lines):
            line = lines[cursor]
            if "configuration" in line.lower():
                numbers = _numbers_from_line(line)
                configuration_indices.append(int(numbers[-1]) if numbers else len(frames) + 1)
                cursor += 1
            if cursor + atom_count > len(lines):
                break
            try:
                frame = np.asarray(
                    [list(map(float, lines[cursor + index].split()[:3])) for index in range(atom_count)],
                    dtype=np.float64,
                )
            except ValueError:
                cursor += 1
                continue
            frames.append(frame)
            cursor += atom_count

        if not frames:
            return self._error_calculation("No XDATCAR trajectory frames were found.")

        direct_positions = np.asarray(frames, dtype=np.float64)
        positions = direct_positions @ header["cell"]
        trajectory = Trajectory.from_arrays(
            species=header["species"],
            positions=positions,
            direct_positions=direct_positions,
            cell=Cell(header["cell"]),
            properties={"format": "XDATCAR"},
        )
        return Calculation(
            source=self.source,
            engine=self.engine,
            trajectory=trajectory,
            properties={
                "file_type": self.__file_type.value,
                "comment": header["comment"],
                "symbols": header["symbols"],
                "counts": header["counts"],
                "configuration_indices": np.asarray(configuration_indices, dtype=np.int64),
            },
        )

    def read_chgcar(self) -> Calculation:
        """Read CHG/CHGCAR structure and the first volumetric data block."""
        lines = _read_nonempty_lines(self.source)
        try:
            parsed = _parse_poscar_lines(lines)
        except ValueError as error:
            return self._error_calculation(str(error))

        cursor = parsed["positions_end"]
        if cursor >= len(lines):
            return self._error_calculation("No charge-density grid was found.")
        grid = np.asarray(list(map(int, lines[cursor].split()[:3])), dtype=np.int64)
        cursor += 1
        value_count = int(np.prod(grid))
        values = []
        while cursor < len(lines) and len(values) < value_count:
            values.extend(_numbers_from_line(lines[cursor]))
            cursor += 1
        if len(values) < value_count:
            return self._error_calculation("Charge-density block ended before the grid was complete.")

        density = np.asarray(values[:value_count], dtype=np.float64).reshape(tuple(grid), order="F")
        trajectory = Trajectory.from_arrays(
            species=parsed["species"],
            positions=parsed["positions"],
            direct_positions=parsed["direct_positions"],
            cell=Cell(parsed["cell"]),
        )
        return Calculation(
            source=self.source,
            engine=self.engine,
            trajectory=trajectory,
            properties={
                "file_type": self.__file_type.value,
                "comment": parsed["comment"],
                "symbols": parsed["symbols"],
                "counts": parsed["counts"],
                "volumetric_data": {
                    "grid": grid,
                    "values": density,
                    "units": "VASP raw charge density",
                },
            },
        )

    def read_oszicar(self) -> Calculation:
        """Read OSZICAR electronic and ionic convergence data."""
        electronic_steps = []
        ionic_steps = []
        current_ionic_index = 0
        for line in self.source.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if ":" in stripped and stripped.split(":", 1)[0].strip().isalpha():
                electronic = _parse_oszicar_electronic_line(stripped, current_ionic_index)
                if electronic is not None:
                    electronic_steps.append(electronic)
                continue
            ionic = _parse_oszicar_ionic_line(stripped)
            if ionic is not None:
                current_ionic_index += 1
                ionic["ionic_step"] = current_ionic_index
                ionic_steps.append(ionic)

        return Calculation(
            source=self.source,
            engine=self.engine,
            properties={
                "file_type": self.__file_type.value,
                "electronic_steps": electronic_steps,
                "ionic_steps": ionic_steps,
            },
        )

    def read_doscar(self) -> Calculation:
        """Read DOSCAR total and projected density-of-states blocks."""
        lines = _read_nonempty_lines(self.source)
        if len(lines) < 6:
            return self._error_calculation("DOSCAR file is too short.")
        first = lines[0].split()
        atom_count = int(first[0]) if first else 0
        header_values = _numbers_from_line(lines[5])
        if len(header_values) < 4:
            return self._error_calculation("DOSCAR header does not contain NEDOS/EFERMI metadata.")
        emax, emin, nedos, efermi = header_values[:4]
        nedos = int(nedos)
        cursor = 6
        total_dos = _read_numeric_block(lines, cursor, nedos)
        cursor += nedos
        projected_dos = []
        for _ in range(atom_count):
            if cursor >= len(lines):
                break
            atom_header = _numbers_from_line(lines[cursor])
            cursor += 1
            if cursor + nedos > len(lines):
                break
            projected_dos.append(
                {
                    "header": np.asarray(atom_header, dtype=np.float64),
                    "data": _read_numeric_block(lines, cursor, nedos),
                }
            )
            cursor += nedos
        return Calculation(
            source=self.source,
            engine=self.engine,
            properties={
                "file_type": self.__file_type.value,
                "atom_count": atom_count,
                "emax": emax,
                "emin": emin,
                "nedos": nedos,
                "efermi": efermi,
                "total_dos": total_dos,
                "projected_dos": projected_dos,
            },
        )

    def read_eigenval(self) -> Calculation:
        """Read EIGENVAL k-point band energies and occupations."""
        lines = _read_nonempty_lines(self.source)
        if len(lines) < 7:
            return self._error_calculation("EIGENVAL file is too short.")
        metadata = list(map(int, lines[5].split()[:3]))
        electron_count, kpoint_count, band_count = metadata
        cursor = 6
        kpoints = []
        weights = []
        bands = []
        for _ in range(kpoint_count):
            while cursor < len(lines) and len(lines[cursor].split()) < 4:
                cursor += 1
            if cursor >= len(lines):
                break
            kpoint_line = list(map(float, lines[cursor].split()[:4]))
            kpoints.append(kpoint_line[:3])
            weights.append(kpoint_line[3])
            cursor += 1
            kpoint_bands = []
            for _ in range(band_count):
                values = _numbers_from_line(lines[cursor])
                if len(values) >= 3:
                    kpoint_bands.append(values[1:])
                cursor += 1
            bands.append(kpoint_bands)
        return Calculation(
            source=self.source,
            engine=self.engine,
            properties={
                "file_type": self.__file_type.value,
                "electron_count": electron_count,
                "kpoint_count": kpoint_count,
                "band_count": band_count,
                "kpoints": np.asarray(kpoints, dtype=np.float64),
                "weights": np.asarray(weights, dtype=np.float64),
                "bands": np.asarray(bands, dtype=np.float64),
            },
        )

    def read_outcar(self) -> Calculation:
        """Read OUTCAR trajectory positions, forces and lattice vectors."""
        counts = []
        symbols = []
        timestep_fs = None
        current_cell = None
        cells = []
        positions = []
        forces = []

        with self.source.open("r", encoding="utf-8", errors="replace") as outcar:
            lines_iter = iter(outcar)
            for line in lines_iter:
                if "POTIM" in line and timestep_fs is None:
                    values = _numbers_from_line(line)
                    if values:
                        timestep_fs = values[0]
                elif "VRHFIN" in line:
                    symbol = line.split("=", 1)[-1].split(":", 1)[0].strip()
                    if symbol:
                        symbols.append(symbol)
                elif "ions per type" in line:
                    counts = [int(value) for value in _numbers_from_line(line)]
                elif "direct lattice vectors" in line:
                    basis = []
                    for _ in range(3):
                        values = _numbers_from_line(next(lines_iter))
                        if len(values) >= 3:
                            basis.append(values[:3])
                    if len(basis) == 3:
                        current_cell = np.asarray(basis, dtype=np.float64)
                elif "POSITION" in line and "TOTAL-FORCE" in line:
                    next(lines_iter, None)
                    frame_positions = []
                    frame_forces = []
                    for row in lines_iter:
                        values = _numbers_from_line(row)
                        if len(values) < 6:
                            break
                        frame_positions.append(values[:3])
                        frame_forces.append(values[3:6])
                    if frame_positions:
                        positions.append(frame_positions)
                        forces.append(frame_forces)
                        if current_cell is not None:
                            cells.append(current_cell)

        if not positions:
            return self._error_calculation("No POSITION/TOTAL-FORCE blocks were found in OUTCAR.")
        atom_count = len(positions[0])
        if not counts:
            counts = [atom_count]
        if not symbols:
            symbols = [f"X{index + 1}" for index in range(len(counts))]
        species = _species_from_symbols_counts(symbols, counts)
        if species.shape[0] != atom_count:
            species = np.asarray([f"X{index + 1}" for index in range(atom_count)], dtype=str)
        if not cells:
            return self._error_calculation("No lattice vectors were found in OUTCAR.")

        positions_array = np.asarray(positions, dtype=np.float64)
        forces_array = np.asarray(forces, dtype=np.float64)
        cells_array = np.asarray(cells, dtype=np.float64)
        trajectory = Trajectory.from_arrays(
            species=species,
            positions=positions_array,
            cell=cells_array if len(cells_array) == len(positions_array) else cells_array[0],
            forces=forces_array,
            timestep_fs=timestep_fs,
            time_fs=np.arange(len(positions_array), dtype=np.float64) * timestep_fs
            if timestep_fs is not None
            else None,
            properties={"format": "OUTCAR"},
        )
        return Calculation(
            source=self.source,
            engine=self.engine,
            trajectory=trajectory,
            properties={"file_type": self.__file_type.value, "symbols": symbols, "counts": counts},
        )

    @staticmethod
    def _read_atominfo_rows(xml, atom_count: int) -> tuple[list[str], list[int]]:
        species: list[str] = []
        atom_types: list[int] = []
        while len(species) < atom_count:
            line = xml.readline()
            if not line:
                break
            values = _TAG_VALUE_RE.findall(line)
            if not values:
                continue
            species.append(values[0].strip())
            try:
                atom_types.append(int(values[-1]))
            except ValueError:
                atom_types.append(0)
        return species, atom_types


def _numbers_from_line(line: str) -> list[float]:
    return [float(value.replace("D", "E").replace("d", "e")) for value in _FLOAT_RE.findall(line)]


def _read_vasp_varray(xml, rows: int) -> list[list[float]]:
    array: list[list[float]] = []
    while len(array) < rows:
        line = xml.readline()
        if not line or "</varray>" in line:
            break
        values = _numbers_from_line(line)
        if len(values) >= 3:
            array.append(values[:3])
    return array


def _read_nonempty_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]


def _parse_poscar_header(lines: list[str]) -> dict:
    if len(lines) < 8:
        raise ValueError("POSCAR-like file is too short.")

    comment = lines[0]
    scale = float(lines[1].split()[0])
    raw_cell = np.asarray(
        [list(map(float, lines[index].split()[:3])) for index in range(2, 5)],
        dtype=np.float64,
    )
    if scale < 0:
        volume = abs(np.linalg.det(raw_cell))
        scale_factor = (-scale / volume) ** (1.0 / 3.0)
        cell_vectors = raw_cell * scale_factor
        position_scale = 1.0
    else:
        cell_vectors = raw_cell * scale
        position_scale = scale

    symbols_line = lines[5].split()
    if _tokens_are_ints(symbols_line):
        counts = list(map(int, symbols_line))
        symbols = [f"X{index + 1}" for index in range(len(counts))]
        cursor = 6
    else:
        symbols = symbols_line
        counts = list(map(int, lines[6].split()))
        cursor = 7

    selective_dynamics = False
    if lines[cursor].lower().startswith("s"):
        selective_dynamics = True
        cursor += 1

    coordinate_mode = lines[cursor].lower()
    cursor += 1

    return {
        "comment": comment,
        "scale": scale,
        "position_scale": position_scale,
        "cell": cell_vectors,
        "symbols": symbols,
        "counts": counts,
        "species": _species_from_symbols_counts(symbols, counts),
        "selective_dynamics": selective_dynamics,
        "coordinate_mode": coordinate_mode,
        "positions_start": cursor,
    }


def _parse_poscar_lines(lines: list[str]) -> dict:
    header = _parse_poscar_header(lines)
    atom_count = int(sum(header["counts"]))
    cursor = header["positions_start"]
    if cursor + atom_count > len(lines):
        raise ValueError("POSCAR-like file does not contain all atom positions.")

    raw_positions = np.asarray(
        [list(map(float, lines[cursor + index].split()[:3])) for index in range(atom_count)],
        dtype=np.float64,
    )
    coordinate_mode = header["coordinate_mode"]
    if coordinate_mode.startswith(("d", "f")):
        direct_positions = raw_positions
        positions = direct_positions @ header["cell"]
    else:
        positions = raw_positions * header["position_scale"]
        direct_positions = positions @ np.linalg.inv(header["cell"])

    header.update(
        {
            "positions": positions,
            "direct_positions": direct_positions,
            "positions_end": cursor + atom_count,
        }
    )
    return header


def _parse_xdatcar_header(lines: list[str]) -> dict:
    if len(lines) < 7:
        raise ValueError("XDATCAR file is too short.")

    comment = lines[0]
    scale = float(lines[1].split()[0])
    raw_cell = np.asarray(
        [list(map(float, lines[index].split()[:3])) for index in range(2, 5)],
        dtype=np.float64,
    )
    cell_vectors = raw_cell * scale
    symbols_line = lines[5].split()
    if _tokens_are_ints(symbols_line):
        counts = list(map(int, symbols_line))
        symbols = [f"X{index + 1}" for index in range(len(counts))]
        cursor = 6
    else:
        symbols = symbols_line
        counts = list(map(int, lines[6].split()))
        cursor = 7

    return {
        "comment": comment,
        "scale": scale,
        "cell": cell_vectors,
        "symbols": symbols,
        "counts": counts,
        "species": _species_from_symbols_counts(symbols, counts),
        "positions_start": cursor,
    }


def _species_from_symbols_counts(symbols: list[str], counts: list[int]) -> np.ndarray:
    return np.asarray(
        [symbol for symbol, count in zip(symbols, counts, strict=False) for _ in range(count)],
        dtype=str,
    )


def _read_numeric_block(lines: list[str], start: int, count: int) -> np.ndarray:
    rows = [_numbers_from_line(lines[index]) for index in range(start, start + count)]
    return np.asarray(rows, dtype=np.float64)


def _parse_oszicar_electronic_line(line: str, ionic_step: int) -> dict | None:
    method, raw_values = line.split(":", 1)
    values = _numbers_from_line(raw_values)
    if len(values) < 2:
        return None
    labels = ["electronic_step", "energy", "dE", "d_eps", "ncg", "rms", "rms_c"]
    parsed = {
        "ionic_step": ionic_step,
        "algorithm": method.strip(),
    }
    for label, value in zip(labels, values, strict=False):
        parsed[label] = int(value) if label in {"electronic_step", "ncg"} else value
    return parsed


def _parse_oszicar_ionic_line(line: str) -> dict | None:
    if "=" not in line:
        return None
    tokens = line.split()
    if not tokens:
        return None
    parsed = {}
    try:
        parsed["step"] = int(tokens[0])
    except ValueError:
        return None
    for index, token in enumerate(tokens):
        if token.endswith("=") and index + 1 < len(tokens):
            key = token[:-1]
            try:
                parsed[key] = _float_from_fortran(tokens[index + 1])
            except ValueError:
                pass
        elif "=" in token:
            key, value = token.split("=", 1)
            if value:
                try:
                    parsed[key] = _float_from_fortran(value)
                except ValueError:
                    pass
    return parsed


def _masses_from_atom_types(atom_types: list[int], pomass_by_type: list[float]) -> np.ndarray | None:
    if not atom_types or not pomass_by_type:
        return None
    masses = []
    for atom_type in atom_types:
        index = atom_type - 1
        masses.append(pomass_by_type[index] if 0 <= index < len(pomass_by_type) else np.nan)
    return np.asarray(masses, dtype=np.float64)


def _tokens_are_ints(tokens: list[str]) -> bool:
    try:
        [int(token) for token in tokens]
    except ValueError:
        return False
    return True


def _float_from_fortran(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e").rstrip(","))


def discover_vasprun_files(directory: str | Path, recursive: bool = False) -> list[Path]:
    """Return vasprun XML files sorted for restart merging."""
    root = Path(directory)
    iterator = root.rglob("vasprun*.xml") if recursive else root.glob("vasprun*.xml")
    return sorted((path for path in iterator if path.is_file()), key=_vasprun_sort_key)


def parse_vasprun_sequence(
    directory: str | Path,
    *,
    recursive: bool = False,
    policy: TrajectoryMergePolicy | None = None,
) -> tuple[Calculation, MergeReport]:
    """Parse and merge all vasprun XML files in a directory."""
    files = discover_vasprun_files(directory, recursive=recursive)
    if not files:
        raise ValueError(f"No vasprun XML files found in {directory}.")
    calculations = [Parser(path).parse() for path in files]
    errors = [calculation for calculation in calculations if calculation.errors.exist]
    if errors:
        first = errors[0]
        raise ValueError(f"Could not parse {first.source}: {first.errors.message}")
    return merge_calculations(calculations, policy or TrajectoryMergePolicy())


def _vasprun_sort_key(path: Path) -> tuple:
    numbers = [int(value) for value in re.findall(r"\d+", path.name)]
    return (0 if numbers else 1, numbers, path.stat().st_mtime, str(path))
