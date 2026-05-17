"""Pydantic schemas used by the FastAPI adapter."""

from __future__ import annotations

from typing import Any, Literal

try:
    from pydantic import BaseModel, ConfigDict, Field, computed_field
except ImportError as exc:  # pragma: no cover - exercised only without web extra
    raise RuntimeError("Install prochem[web] to use the web schemas.") from exc

from prochem.core import Calculation
from prochem.rendering import SceneData


Vec3Schema = tuple[float, float, float]
ColorSchema = tuple[float, float, float, float]


class WebSchema(BaseModel):
    """Base config shared by web-facing schemas."""

    model_config = ConfigDict(extra="forbid")


class AtomPrimitiveSchema(WebSchema):
    atom_id: int
    symbol: str
    position: Vec3Schema
    radius: float
    color: ColorSchema


class BondPrimitiveSchema(WebSchema):
    first_atom_id: int
    second_atom_id: int
    radius: float = 0.08
    color: ColorSchema = (0.7, 0.7, 0.7, 1.0)


class CellPrimitiveSchema(WebSchema):
    vectors: tuple[Vec3Schema, Vec3Schema, Vec3Schema]
    color: ColorSchema = (0.6, 0.6, 0.6, 1.0)


class AxesPrimitiveSchema(WebSchema):
    origin: Vec3Schema = (0.0, 0.0, 0.0)
    length: float = 1.0
    labels: tuple[str, str, str] = ("x", "y", "z")


class PrimitiveSetSchema(WebSchema):
    atoms: list[AtomPrimitiveSchema] = Field(default_factory=list)
    bonds: list[BondPrimitiveSchema] = Field(default_factory=list)
    cell: CellPrimitiveSchema | None = None
    axes: AxesPrimitiveSchema | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SceneDataSchema(WebSchema):
    frames: list[PrimitiveSetSchema]
    name: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @classmethod
    def from_scene_data(cls, scene: SceneData) -> "SceneDataSchema":
        """Validate and serialize a backend-independent scene DTO."""
        return cls.model_validate(scene.to_dict())


class SceneOptionsSchema(WebSchema):
    frame_indices: list[int] | None = None
    include_bonds: bool = True
    include_cell: bool = True
    include_axes: bool = True
    atom_radius_scale: float = Field(default=0.35, gt=0.0)
    bond_radius: float = Field(default=0.08, gt=0.0)
    bond_scale: float = Field(default=1.25, gt=0.0)
    max_atoms_for_bonds: int = Field(default=500, ge=0)

    def to_scene_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments accepted by rendering.scene helpers."""
        data = self.model_dump()
        if data["frame_indices"] is not None:
            data["frame_indices"] = tuple(data["frame_indices"])
        return data


class CalculationSummary(WebSchema):
    name: str
    engine: str
    source: str
    kind: Literal["trajectory", "dataset", "structure", "empty"]
    step_count: int
    structure_count: int
    atom_count: int
    warnings: list[str] = Field(default_factory=list)
    has_errors: bool = False
    error_message: str = ""

    @classmethod
    def from_calculation(cls, calculation: Calculation) -> "CalculationSummary":
        """Build a compact response object for parsed calculations."""
        if calculation.trajectory is not None:
            kind: Literal["trajectory", "dataset", "structure", "empty"] = "trajectory"
        elif calculation.dataset is not None:
            kind = "dataset"
        elif calculation.structure is not None:
            kind = "structure"
        else:
            kind = "empty"
        return cls(
            name=calculation.name,
            engine=calculation.engine,
            source=str(calculation.source),
            kind=kind,
            step_count=calculation.step_count,
            structure_count=calculation.structure_count,
            atom_count=calculation.atom_count,
            warnings=list(calculation.warnings),
            has_errors=calculation.errors.exist,
            error_message=calculation.errors.message,
        )


class ParseRequestSchema(WebSchema):
    path: str
    parser: str | None = None
    scene: SceneOptionsSchema | None = Field(default_factory=SceneOptionsSchema)


class ParseResponseSchema(WebSchema):
    calculation: CalculationSummary
    scene: SceneDataSchema | None = None


class HealthResponseSchema(WebSchema):
    status: Literal["ok"]


__all__ = [
    "AtomPrimitiveSchema",
    "AxesPrimitiveSchema",
    "BondPrimitiveSchema",
    "CalculationSummary",
    "CellPrimitiveSchema",
    "ColorSchema",
    "HealthResponseSchema",
    "ParseRequestSchema",
    "ParseResponseSchema",
    "PrimitiveSetSchema",
    "SceneDataSchema",
    "SceneOptionsSchema",
    "Vec3Schema",
]
