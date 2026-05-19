"""Atom domain object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np

from prochem.core.periodic_table import element, normalize_symbol

ArrayLike = np.ndarray


@dataclass(slots=True)
class SharedFloat:
    """Mutable float value shared by atoms of the same element."""

    value: float

    def __float__(self) -> float:
        return float(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SharedFloat):
            return self.value == other.value
        if isinstance(other, int | float):
            return self.value == float(other)
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass(slots=True)
class AtomStyle:
    size: SharedFloat
    color: ArrayLike


_STYLE_BY_NAME: dict[str, AtomStyle] = {}


def _vector3(values: Iterable[float] | None, field_name: str) -> ArrayLike:
    if values is None:
        return np.zeros(3, dtype=np.float64)
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (3,):
        raise ValueError(f"Atom {field_name} must have shape (3,), got {array.shape}.")
    return array


def _color4(values: Iterable[float]) -> ArrayLike:
    array = np.asarray(values, dtype=np.float64)
    if array.shape == (3,):
        array = np.asarray([array[0], array[1], array[2], 1.0], dtype=np.float64)
    if array.shape != (4,):
        raise ValueError(f"Atom color must have shape (4,), got {array.shape}.")
    if np.any(array[:3] > 1.0):
        array[:3] = array[:3] / 255.0
    return np.clip(array, 0.0, 1.0)


def element_style(name: str | int) -> AtomStyle:
    symbol = normalize_symbol(name)
    style = _STYLE_BY_NAME.get(symbol)
    if style is not None:
        return style
    item = element(symbol)
    if item is None:
        style = AtomStyle(size=SharedFloat(0.75), color=np.asarray((0.6, 0.6, 0.6, 1.0)))
    else:
        style = AtomStyle(
            size=SharedFloat(float(item.covalent_radius)),
            color=np.asarray(item.color, dtype=np.float64),
        )
    _STYLE_BY_NAME[symbol] = style
    return style


@dataclass(init=False, slots=True)
class Atom:
    """One atom with element defaults and mutable per-atom state."""

    index: int
    name: str
    position: ArrayLike
    direct_position: ArrayLike
    velocity: ArrayLike
    force: ArrayLike
    potential_energy: float | None
    kinetic_energy: float | None
    _total_energy: float | None = field(repr=False)
    charge: int
    valent_charge: int
    mass: float
    _size: SharedFloat = field(repr=False)
    _color: ArrayLike = field(repr=False)
    properties: dict[str, Any]

    def __init__(
        self,
        name: str | int | None = None,
        *,
        index: int | None = None,
        position: Iterable[float] | None = None,
        direct_position: Iterable[float] | None = None,
        velocity: Iterable[float] | None = None,
        force: Iterable[float] | None = None,
        potential_energy: float | None = None,
        kinetic_energy: float | None = None,
        total_energy: float | None = None,
        charge: int | None = None,
        valent_charge: int | None = None,
        mass: float | None = None,
        size: float | SharedFloat | None = None,
        color: Iterable[float] | None = None,
        properties: dict[str, Any] | None = None,
        species: str | int | None = None,
        atom_id: int | None = None,
        initial_index: int | None = None,
    ) -> None:
        raw_name = name if name is not None else (species if species is not None else "X")
        symbol = normalize_symbol(raw_name)
        item = element(symbol)
        if item is None and symbol == "X":
            default_charge = 0
            default_valent_charge = 0
            default_mass = 0.0
        elif item is None:
            default_charge = 0
            default_valent_charge = 0
            default_mass = 0.0
        else:
            default_charge = item.atomic_number
            default_valent_charge = item.valence_charge
            default_mass = item.mass

        if index is None:
            index = (
                atom_id
                if atom_id is not None
                else (initial_index if initial_index is not None else 0)
            )

        self.index = int(index)
        self.name = symbol
        self.position = _vector3(position, "position")
        self.direct_position = _vector3(direct_position, "direct_position")
        self.velocity = _vector3(velocity, "velocity")
        self.force = _vector3(force, "force")
        self.potential_energy = _optional_float(potential_energy)
        self.kinetic_energy = _optional_float(kinetic_energy)
        self._total_energy = _optional_float(total_energy)
        self.charge = default_charge if charge is None else int(charge)
        self.valent_charge = default_valent_charge if valent_charge is None else int(valent_charge)
        self.mass = default_mass if mass is None else float(mass)
        style = element_style(symbol)
        self._size = style.size if not isinstance(size, SharedFloat) else size
        self._color = style.color
        if size is not None and not isinstance(size, SharedFloat):
            self.size = float(size)
        if color is not None:
            self.color = color
        self.properties = {} if properties is None else dict(properties)
        for key, provided, value in (
            ("direct_position", direct_position is not None, self.direct_position),
            ("velocity", velocity is not None, self.velocity),
            ("force", force is not None, self.force),
            ("potential_energy", potential_energy is not None, self.potential_energy),
            ("kinetic_energy", kinetic_energy is not None, self.kinetic_energy),
            ("total_energy", total_energy is not None, self.total_energy),
        ):
            if provided and value is not None:
                self.properties.setdefault(key, True)

    @property
    def size(self) -> SharedFloat:
        return self._size

    @size.setter
    def size(self, value: float | SharedFloat) -> None:
        if isinstance(value, SharedFloat):
            self._size = value
        else:
            self._size.value = float(value)

    @property
    def color(self) -> ArrayLike:
        return self._color

    @color.setter
    def color(self, value: Iterable[float]) -> None:
        self._color[:] = _color4(value)

    @property
    def atom_id(self) -> int:
        return self.index

    @atom_id.setter
    def atom_id(self, value: int) -> None:
        self.index = int(value)

    @property
    def initial_index(self) -> int:
        return self.index

    @property
    def species(self) -> str:
        return self.name

    @species.setter
    def species(self, value: str | int) -> None:
        self.name = normalize_symbol(value)

    def approximate_force(
        self,
        next_velocity: Iterable[float],
        delta_t: float,
        *,
        update: bool = False,
    ) -> ArrayLike:
        """Approximate force from the velocity change over ``delta_t``."""
        if delta_t == 0:
            raise ValueError("delta_t must be non-zero.")
        force = self.mass * (_vector3(next_velocity, "next_velocity") - self.velocity) / float(delta_t)
        if update:
            self.force = force.copy()
            self.properties["force"] = True
        return force

    def kinetic_energy_from_velocity(
        self,
        velocity: Iterable[float] | None = None,
        *,
        update: bool = False,
    ) -> float:
        """Return classical kinetic energy ``0.5 * mass * |velocity|^2``."""
        values = self.velocity if velocity is None else _vector3(velocity, "velocity")
        energy = 0.5 * self.mass * float(np.dot(values, values))
        if update:
            self.kinetic_energy = energy
            self.properties["kinetic_energy"] = True
        return energy

    @property
    def total_energy(self) -> float | None:
        if self._total_energy is not None:
            return self._total_energy
        if self.potential_energy is None or self.kinetic_energy is None:
            return None
        return self.potential_energy + self.kinetic_energy

    @total_energy.setter
    def total_energy(self, value: float | None) -> None:
        self._total_energy = _optional_float(value)

    def copy(self, **changes: Any) -> "Atom":
        params = {
            "name": self.name,
            "index": self.index,
            "position": self.position.copy(),
            "direct_position": self.direct_position.copy(),
            "velocity": self.velocity.copy(),
            "force": self.force.copy(),
            "potential_energy": self.potential_energy,
            "kinetic_energy": self.kinetic_energy,
            "total_energy": self._total_energy,
            "charge": self.charge,
            "valent_charge": self.valent_charge,
            "mass": self.mass,
            "size": self._size,
            "color": self._color.copy(),
            "properties": dict(self.properties),
        }
        params.update(changes)
        atom = Atom(**params)
        if "color" not in changes:
            atom._color = self._color
        return atom

    def __repr__(self) -> str:
        parts = [
            f"index={self.index}",
            f"name='{self.name}'",
            f"position={_format_vector(self.position)}",
        ]
        if _has_vector_value(self.direct_position) or "direct_position" in self.properties:
            parts.append(f"direct_position={_format_vector(self.direct_position)}")
        if _has_vector_value(self.velocity) or "velocity" in self.properties:
            parts.append(f"velocity={_format_vector(self.velocity)}")
        if _has_vector_value(self.force) or "force" in self.properties:
            parts.append(f"force={_format_vector(self.force)}")
        if self.potential_energy is not None or "potential_energy" in self.properties:
            parts.append(f"potential_energy={_format_float(self.potential_energy)}")
        if self.kinetic_energy is not None or "kinetic_energy" in self.properties:
            parts.append(f"kinetic_energy={_format_float(self.kinetic_energy)}")
        if self.total_energy is not None or "total_energy" in self.properties:
            parts.append(f"total_energy={_format_float(self.total_energy)}")
        parts.extend(
            [
                f"mass={_format_float(self.mass)}",
                f"charge={self.charge}",
                f"valent_charge={self.valent_charge}",
            ]
        )
        return f"Atom({', '.join(parts)})"


def _has_vector_value(values: ArrayLike) -> bool:
    return bool(np.any(np.asarray(values, dtype=np.float64) != 0.0))


def _optional_float(value: float | None) -> float | None:
    if value is None:
        return None
    result = float(value)
    return None if np.isnan(result) else result


def _format_float(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{float(value):.6g}"


def _format_vector(values: Iterable[float]) -> str:
    return "(" + ", ".join(_format_float(value) for value in values) + ")"


__all__ = ["Atom", "AtomStyle", "SharedFloat", "element_style"]
