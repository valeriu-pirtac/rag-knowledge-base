from typing import Any
from fastapi import APIRouter, Depends

from app.config import get_settings
from app.config.settings import Settings


router = APIRouter()


@router.get("/health-check")
def health_check(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    return {
        "env.type": settings.env.type,
        "app.name": settings.app.name,
        "api.version": settings.api.version,
    }
