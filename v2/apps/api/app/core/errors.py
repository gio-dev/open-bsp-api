"""Canonical API error body (CDA D4)."""

from __future__ import annotations

from typing import Any

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field


class CanonicalErrorResponse(BaseModel):
    """Envelope JSON unico para erros HTTP (alinhado a `canonical_error_body`)."""

    code: str = Field(examples=["http_403"])
    message: str
    request_id: str


class FieldErrorItem(BaseModel):
    """Um campo com falha de validacao (Story 1.3 / AC5)."""

    field: str
    message: str


class CanonicalValidationErrorResponse(BaseModel):
    """422: envelope canonico + erros por campo para clientes (admin-web)."""

    code: str = Field(examples=["validation_error"])
    message: str
    request_id: str
    errors: list[FieldErrorItem] = Field(default_factory=list)


def canonical_error_body(*, code: str, message: str, request_id: str) -> dict[str, str]:
    return {
        "code": code,
        "message": message,
        "request_id": request_id,
    }


def field_errors_from_request_validation(
    exc: RequestValidationError,
) -> list[dict[str, str]]:
    """Extrai lista estavel field/message a partir do RequestValidationError."""
    skip_root = {"body", "query", "path", "header"}
    out: list[dict[str, str]] = []
    for err in exc.errors():
        loc: tuple[Any, ...] = tuple(err.get("loc") or ())
        field = "body"
        for part in reversed(loc):
            if isinstance(part, str) and part not in skip_root:
                field = part
                break
            if isinstance(part, int):
                field = f"index_{part}"
                break
        msg = err.get("msg", "invalid")
        out.append({"field": field, "message": str(msg)})
    return out


def canonical_validation_error_body(
    *,
    message: str,
    request_id: str,
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "code": "validation_error",
        "message": message,
        "request_id": request_id,
        "errors": errors,
    }
