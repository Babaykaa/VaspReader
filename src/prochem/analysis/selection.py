"""Atom selections used by pandas-based analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Selection:
    """Named set of stable atom ids.

    ``atom_ids`` are global ids from :class:`prochem.core.Structures`, not local
    positions inside one frame. This keeps selections stable when a later frame
    is missing an atom after a restart.
    """

    name: str
    atom_ids: tuple[int, ...]

    def __init__(self, name: str, atom_ids: Iterable[int]) -> None:
        ids = tuple(dict.fromkeys(int(atom_id) for atom_id in atom_ids))
        if not name:
            raise ValueError("Selection name must not be empty.")
        if not ids:
            raise ValueError("Selection must contain at least one atom id.")
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "atom_ids", ids)

    @classmethod
    def single(cls, atom_id: int, *, name: str | None = None) -> "Selection":
        return cls(str(atom_id) if name is None else name, (atom_id,))

    def __contains__(self, atom_id: object) -> bool:
        try:
            return int(atom_id) in self.atom_ids
        except (TypeError, ValueError):
            return False

    def __len__(self) -> int:
        return len(self.atom_ids)


__all__ = ["Selection"]
