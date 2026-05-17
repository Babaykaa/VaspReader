from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from prochem.adapters.web.api import create_app  # noqa: E402
from prochem.adapters.web.schemas import HealthResponseSchema  # noqa: E402


def test_create_app_exposes_typed_health_route() -> None:
    app = create_app()

    route = next(route for route in app.routes if getattr(route, "path", None) == "/health")

    assert app.title == "ProChem"
    assert route.response_model is HealthResponseSchema
