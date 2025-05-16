import pathlib

from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILEPATH = pathlib.Path(__file__).parent.parent.parent / ".env"


class ApiPrefixConfig(BaseModel):
    prefix: str = "/api"


class RunConfig(BaseModel):
    host: str = None
    port: int = None


class AuthConfig(BaseModel):
    secret_key: str = None
    algorithm: str = None
    access_token_expire_min: int = None


class DatabaseConfig(BaseModel):
    host: str = None
    port: str = None
    name: str = None
    user: str = None
    password: str = None
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @computed_field
    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="allow",
    )

    run: RunConfig = RunConfig()
    api_prefix: ApiPrefixConfig = ApiPrefixConfig()
    auth: AuthConfig = AuthConfig()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings(_env_file=ENV_FILEPATH)
