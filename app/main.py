from fastapi import FastAPI

from app.api.v1 import register_routers
from app.config import get_settings
from app.config.settings import Settings


settings: Settings = get_settings()
app = FastAPI(
    title=settings.app.name,
    debug=settings.debug_enabled,
    root_path=f"/api/{settings.api.version}",
)

register_routers(app)
