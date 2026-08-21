"""HTTP: список метаданных записей и аудио 200 / 409."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.services.recordings import (
    InMemoryRecordingsService,
    RecordingsService,
    get_default_recordings_service,
)

router = APIRouter(tags=["recordings"])


class RecordingsPage(BaseModel):
    items: list[dict[str, Any]]
    page: int
    page_size: int
    total: int


async def get_recordings_service() -> RecordingsService:
    svc = get_default_recordings_service()
    if isinstance(svc, InMemoryRecordingsService) and not svc._rows:  # noqa: SLF001
        await svc.load_fixtures()
    return svc


@router.get("/recordings", response_model=RecordingsPage)
async def list_recordings(
    svc: Annotated[RecordingsService, Depends(get_recordings_service)],
    page: int = 1,
    page_size: int = 25,
    ucid: str | None = None,
    encrypted: Annotated[bool | None, Query()] = None,
) -> dict[str, Any]:
    return await svc.list_page(page=page, page_size=page_size, ucid=ucid, encrypted=encrypted)


@router.get("/recordings/{recording_id}")
async def get_recording(
    recording_id: int,
    svc: Annotated[RecordingsService, Depends(get_recordings_service)],
) -> dict[str, Any]:
    row = await svc.get(recording_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Recording not found"},
        )
    return row


@router.get(
    "/recordings/{recording_id}/audio",
    responses={
        200: {"content": {"audio/wav": {}, "application/octet-stream": {}}},
        409: {
            "description": "Encrypted IPO R11.1+ recording — metadata only",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": "recording_encrypted",
                            "message": "IP Office recording is encrypted (R11.1+). Metadata only.",
                            "reason": "ipo_encrypted_r11",
                        },
                        "recording": {"id": 1, "encrypted": True, "ucid": "..."},
                    }
                }
            },
        },
    },
)
async def get_recording_audio(
    recording_id: int,
    svc: Annotated[RecordingsService, Depends(get_recordings_service)],
) -> Response:
    result = await svc.get_audio(recording_id)
    if isinstance(result, tuple):
        mime, data = result
        return Response(content=data, media_type=mime, headers={"Accept-Ranges": "bytes"})
    err = result.get("error")
    if err == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Recording not found"},
        )
    if err == "encrypted":
        body = {
            "error": {
                "code": "recording_encrypted",
                "message": "IP Office recording is encrypted (R11.1+). Metadata only.",
                "reason": "ipo_encrypted_r11",
            },
            "recording": result.get("recording"),
        }
        return JSONResponse(status_code=409, content=body)
    raise HTTPException(
        status_code=404,
        detail={"code": "audio_missing", "message": "Audio file not found"},
    )
