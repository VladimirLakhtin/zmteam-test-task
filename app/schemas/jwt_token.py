"""JWT token schema module."""

from pydantic import BaseModel


class TokenData(BaseModel):
    """Schema for JWT token payload data.

    Attributes:
        username (str | None): Username associated with the token
    """
    username: str | None = None
