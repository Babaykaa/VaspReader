"""Backend-independent rendering primitives."""

from __future__ import annotations

from dataclasses import dataclass, field


Color = tuple[float, float, float, float]
Vec3 = tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class AtomPrimitive:
    atom_id: int
    symbol: str
    position: Vec3
    radius: float
    color: Color
    image_of_atom_id: int | None = None
    image_shift: tuple[int, int, int] | None = None


@dataclass(frozen=True, slots=True)
class BondPrimitive:
    first_atom_id: int
    second_atom_id: int
    radius: float = 0.08
    color: Color = (0.7, 0.7, 0.7, 1.0)
    start: Vec3 | None = None
    end: Vec3 | None = None
    image_shift: tuple[int, int, int] | None = None


@dataclass(frozen=True, slots=True)
class CellPrimitive:
    vectors: tuple[Vec3, Vec3, Vec3]
    color: Color = (0.6, 0.6, 0.6, 1.0)


@dataclass(frozen=True, slots=True)
class AxesPrimitive:
    origin: Vec3 = (0.0, 0.0, 0.0)
    length: float = 1.0
    labels: tuple[str, str, str] = ("x", "y", "z")


@dataclass(frozen=True, slots=True)
class PrimitiveSet:
    atoms: tuple[AtomPrimitive, ...] = field(default_factory=tuple)
    bonds: tuple[BondPrimitive, ...] = field(default_factory=tuple)
    cell: CellPrimitive | None = None
    axes: AxesPrimitive | None = None
    metadata: dict[str, object] = field(default_factory=dict)
