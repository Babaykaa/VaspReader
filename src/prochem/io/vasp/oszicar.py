"""OSZICAR parser."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from prochem.core.models import Calculation
from prochem.core.results import ElectronicStep, ElectronicSteps, IonicStep, IonicSteps
from prochem.io.vasp.common import VASPfileType, float_from_fortran, numbers_from_line


def read_oszicar(source: Path, file_type: VASPfileType = VASPfileType.OSZICAR, engine: str = "vasp") -> Calculation:
    """Read OSZICAR electronic and ionic convergence data."""
    electronic_steps = []
    ionic_steps = []
    current_ionic_index = 0
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" in stripped and stripped.split(":", 1)[0].strip().isalpha():
            electronic = parse_oszicar_electronic_line(stripped, current_ionic_index)
            if electronic is not None:
                electronic_steps.append(electronic)
            continue
        ionic = parse_oszicar_ionic_line(stripped)
        if ionic is not None:
            current_ionic_index += 1
            ionic_steps.append(replace(ionic, ionic_step=current_ionic_index))

    return Calculation(
        source=source,
        engine=engine,
        properties={
            "file_type": file_type.value,
            "electronic_steps": ElectronicSteps(electronic_steps),
            "ionic_steps": IonicSteps(ionic_steps),
        },
    )


def parse_oszicar_electronic_line(line: str, ionic_step: int) -> ElectronicStep | None:
    method, raw_values = line.split(":", 1)
    values = numbers_from_line(raw_values)
    if len(values) < 2:
        return None
    labels = ["electronic_step", "energy", "dE", "d_eps", "ncg", "rms", "rms_c"]
    parsed = {
        "ionic_step": ionic_step,
        "algorithm": method.strip(),
    }
    for label, value in zip(labels, values, strict=False):
        parsed[label] = int(value) if label in {"electronic_step", "ncg"} else value
    return ElectronicStep.from_mapping(parsed)


def parse_oszicar_ionic_line(line: str) -> IonicStep | None:
    if "=" not in line:
        return None
    tokens = line.replace("=", " = ").split()
    if not tokens:
        return None
    parsed = {}
    try:
        parsed["step"] = int(tokens[0])
    except ValueError:
        return None
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if (
            token == "d"
            and index + 3 < len(tokens)
            and tokens[index + 1] == "E"
            and tokens[index + 2] == "="
        ):
            try:
                parsed["dE"] = float_from_fortran(tokens[index + 3])
            except ValueError:
                pass
            index += 4
            continue
        if index + 2 < len(tokens) and tokens[index + 1] == "=":
            key = token
            try:
                parsed[key] = float_from_fortran(tokens[index + 2])
            except ValueError:
                pass
            index += 3
            continue
        index += 1
    return IonicStep.from_mapping(parsed)
