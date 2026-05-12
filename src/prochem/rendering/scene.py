"""Scene DTOs shared by Qt, Jupyter and web renderers."""

from __future__ import annotations

from dataclasses import dataclass, field

from prochem.rendering.primitives import PrimitiveSet


@dataclass(frozen=True, slots=True)
class SceneData:
    frames: tuple[PrimitiveSet, ...]
    name: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def frame_count(self) -> int:
        return len(self.frames)

