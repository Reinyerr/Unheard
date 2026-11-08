"""Local health and confirmation/retry/referral API; no provider calls at bootstrap."""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routes.recovery import router as recovery_router
from app.services.recovery_state import RecoveryService

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def cors_origins() -> list[str]:
    origins = os.getenv(
        "UNHEARD_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    result = []
    for value in origins:
        origin = value.strip()
        url = urlsplit(origin)
        if (
            url.scheme != "http"
            or url.hostname not in {"localhost", "127.0.0.1"}
            or url.port is None
            or url.username is not None
            or url.password is not None
            or url.path or url.query or url.fragment
        ):
            raise ValueError("UNHEARD_CORS_ORIGINS must contain exact HTTP loopback origins with ports")
        result.append(origin)
    return result


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    mode: Literal["local"] = "local"


def create_app() -> FastAPI:
    app = FastAPI(title="UNHEARD", version="0.1.0")
    app.state.recovery_service = RecoveryService()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    app.include_router(recovery_router)
    return app


app = create_app()
