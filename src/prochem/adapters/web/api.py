"""FastAPI adapter factory."""

from __future__ import annotations


def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install prochem[web] to use the web adapter.") from exc

    app = FastAPI(title="ProChem")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app

