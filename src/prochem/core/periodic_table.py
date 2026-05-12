"""Small periodic-table metadata used by parsers and renderers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Element:
    symbol: str
    atomic_number: int
    mass: float
    covalent_radius: float
    vdw_radius: float
    color: tuple[float, float, float]


ELEMENTS: dict[str, Element] = {
    "H": Element("H", 1, 1.008, 0.31, 1.20, (1.0, 1.0, 1.0)),
    "C": Element("C", 6, 12.011, 0.76, 1.70, (0.2, 0.2, 0.2)),
    "N": Element("N", 7, 14.007, 0.71, 1.55, (0.05, 0.05, 1.0)),
    "O": Element("O", 8, 15.999, 0.66, 1.52, (1.0, 0.05, 0.05)),
    "F": Element("F", 9, 18.998, 0.57, 1.47, (0.55, 0.85, 0.35)),
    "Si": Element("Si", 14, 28.085, 1.11, 2.10, (0.85, 0.65, 0.45)),
    "S": Element("S", 16, 32.06, 1.05, 1.80, (1.0, 0.9, 0.15)),
    "Ar": Element("Ar", 18, 39.948, 1.06, 1.88, (0.5, 0.8, 0.9)),
    "Mo": Element("Mo", 42, 95.95, 1.54, 2.10, (0.45, 0.55, 0.6)),
}


def element(symbol: str) -> Element | None:
    """Return metadata for an element symbol when it is known."""
    return ELEMENTS.get(symbol.capitalize())


def atomic_mass(symbol: str) -> float | None:
    item = element(symbol)
    return None if item is None else item.mass


def covalent_radius(symbol: str) -> float | None:
    item = element(symbol)
    return None if item is None else item.covalent_radius

