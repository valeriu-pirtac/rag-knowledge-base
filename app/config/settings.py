from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from enum import StrEnum

from app.config.consts import EMPTY


class EnvType(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Env(BaseModel):
    type: EnvType = Field(default=EnvType.DEV)


class App(BaseModel):
    name: str = Field(default=EMPTY)


class Api(BaseModel):
    version: str = Field(default="v1")


class Settings(BaseSettings):
    env: Env = Env()
    app: App = App()
    api: Api = Api()

    @property
    def debug_enabled(self) -> bool:
        return self.env in [EnvType.DEV, EnvType.TEST]

    model_config = SettingsConfigDict(
        env_nested_delimiter=".",
        env_file=(".env", ".env.dev", ".env.test", ".env.prod"),
        env_file_encoding="utf-8",
    )
