"""Serialization helpers for portable ProChem data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_json(data: dict[str, Any], path: str | Path) -> Path:
    output = Path(path)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return output


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

