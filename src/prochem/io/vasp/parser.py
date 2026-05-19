"""VASP parser router."""

from __future__ import annotations

import logging
import traceback
from pathlib import Path

from prochem.core.models import Calculation
from prochem.io.base import AbstractParser
from prochem.io.vasp.common import VASPfileType
from prochem.io.vasp.doscar import read_doscar
from prochem.io.vasp.eigenval import read_eigenval
from prochem.io.vasp.oszicar import read_oszicar
from prochem.io.vasp.outcar import read_outcar
from prochem.io.vasp.poscar import read_chgcar, read_poscar, read_xdatcar
from prochem.io.vasp.vasprun import discover_vasprun_files, parse_vasprun_sequence, read_vasprun

logger = logging.getLogger(__name__)

__all__ = [
    "Parser",
    "VASPfileType",
    "discover_vasprun_files",
    "parse_vasprun_sequence",
]


class Parser(AbstractParser):
    """Parser for VASP structure, structure-sequence and result files."""

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
        return read_vasprun(self.source, self.__file_type, self.engine)

    def read_poscar(self) -> Calculation:
        return read_poscar(self.source, self.__file_type, self.engine)

    def read_xdatcar(self) -> Calculation:
        return read_xdatcar(self.source, self.__file_type, self.engine)

    def read_chgcar(self) -> Calculation:
        return read_chgcar(self.source, self.__file_type, self.engine)

    def read_oszicar(self) -> Calculation:
        return read_oszicar(self.source, self.__file_type, self.engine)

    def read_doscar(self) -> Calculation:
        return read_doscar(self.source, self.__file_type, self.engine)

    def read_eigenval(self) -> Calculation:
        return read_eigenval(self.source, self.__file_type, self.engine)

    def read_outcar(self) -> Calculation:
        return read_outcar(self.source, self.__file_type, self.engine)

