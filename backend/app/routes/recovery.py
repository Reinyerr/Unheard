"""JSON-only, bounded recovery routes with safe error envelopes."""
from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.schemas.recovery import (
    CapabilitiesResponse, DecisionRequest, RecoveryResponse, RetryRequest, SessionId, StartRequest,
)
from app.services.recovery_state import RecoveryError, RecoveryService


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message, "retryable": False}}, status_code=status)


class BoundedRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks, size = [], 0
            async for chunk in self.stream():
                size += len(chunk)
                if size > 4096:
                    raise HTTPException(413, "JSON payload exceeds 4096 bytes")
                chunks.append(chunk)
            self._body = b"".join(chunks)
        return self._body


class RecoveryRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()
        async def handler(request: Request):
            try:
                if request.method == "POST":
                    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
                        return error_response("invalid_content_type", "Use application/json; uploads are not accepted", 415)
                    if request.headers.get("content-encoding", "identity") != "identity":
                        return error_response("invalid_content_encoding", "Compressed request bodies are not accepted", 415)
                    request = BoundedRequest(request.scope, request.receive)
                    await request.body()
                return await original(request)
            except RecoveryError as exc:
                content = {"error": exc.detail.model_dump(mode="json")}
                if exc.session is not None:
                    content["session"] = exc.session.model_dump(mode="json")
                return JSONResponse(content, status_code=exc.status)
            except RequestValidationError:
                return error_response("invalid_request", "Request fields or values are invalid", 422)
            except HTTPException as exc:
                return error_response("payload_too_large" if exc.status_code == 413 else "invalid_request",
                                      "JSON payload exceeds 4096 bytes" if exc.status_code == 413 else "Malformed JSON request", exc.status_code)
        return handler


router = APIRouter(prefix="/api/recovery", tags=["recovery"], route_class=RecoveryRoute)


def service(request: Request) -> RecoveryService:
    return request.app.state.recovery_service


@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities(request: Request):
    return service(request).capabilities()


@router.post("/start", response_model=RecoveryResponse)
def start(payload: StartRequest, request: Request):
    return service(request).start(payload)


@router.post("/decision", response_model=RecoveryResponse)
def decision(payload: DecisionRequest, request: Request):
    return service(request).decide(payload)


@router.post("/retry", response_model=RecoveryResponse)
def retry(payload: RetryRequest, request: Request):
    return service(request).retry(payload)


@router.get("/sessions/{session_id}", response_model=RecoveryResponse)
def session(session_id: SessionId, request: Request):
    return service(request).get(session_id)
