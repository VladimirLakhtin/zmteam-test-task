"""Configuration module."""

import pathlib

from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILEPATH = pathlib.Path(__file__).parent.parent.parent / ".env"


class ApiPrefixConfig(BaseModel):
    """API prefix configuration.
    
    This class defines the URL prefixes for different API sections.
    
    Attributes:
        api (str): Base API prefix
        tasks (str): Tasks API prefix
    """
    api: str = "/api"
    tasks: str = "/tasks"


class RunConfig(BaseModel):
    """Application run configuration.
    
    This class defines the host and port settings for the application server.
    
    Attributes:
        host (str): Server host address
        port (int): Server port number
    """
    host: str = None
    port: int = None


class AuthConfig(BaseModel):
    """Authentication configuration.
    
    This class defines settings for JWT authentication.
    
    Attributes:
        secret_key (str): Secret key for JWT token signing
        algorithm (str): Algorithm used for JWT token signing
        access_token_expire_min (int): Token expiration time in minutes
    """
    secret_key: str = None
    algorithm: str = None
    access_token_expire_min: int = None


class DatabaseConfig(BaseModel):
    """Database configuration.
    
    This class defines settings for database connection and connection pool.
    
    Attributes:
        host (str): Database host address
        port (str): Database port number
        name (str): Database name
        user (str): Database user
        password (str): Database password
        echo (bool): Enable SQL query logging
        echo_pool (bool): Enable connection pool logging
        pool_size (int): Size of the connection pool
        max_overflow (int): Maximum number of connections that can be created beyond the pool size
    """
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
        """Get database connection string.
        
        Returns:
            str: PostgreSQL connection string with asyncpg driver
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    """Application settings.
    
    This class combines all configuration sections and handles loading
    from environment variables and .env file.
    
    Attributes:
        run (RunConfig): Server run configuration
        api_prefix (ApiPrefixConfig): API prefix configuration
        auth (AuthConfig): Authentication configuration
        db (DatabaseConfig): Database configuration
    """
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
