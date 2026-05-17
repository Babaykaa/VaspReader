"""FastAPI adapter factory."""

from __future__ import annotations


def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install prochem[web] to use the web adapter.") from exc

    from prochem.adapters.web.schemas import HealthResponseSchema

    app = FastAPI(title="ProChem")

    @app.get("/health", response_model=HealthResponseSchema)
    def health() -> HealthResponseSchema:
        return HealthResponseSchema(status="ok")

    return app
