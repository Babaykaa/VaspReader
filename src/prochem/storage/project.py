"""Project-state persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from prochem.storage.serialization import load_json, save_json


@dataclass(slots=True)
class ProjectState:
    name: str
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


def save_project(project: ProjectState, path: str | Path) -> Path:
    return save_json(asdict(project), path)


def load_project(path: str | Path) -> ProjectState:
    data = load_json(path)
    return ProjectState(
        name=data["name"],
        sources=list(data.get("sources", [])),
        metadata=dict(data.get("metadata", {})),
    )

