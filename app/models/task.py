"""Task model module."""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def utc_now() -> datetime:
    """Get current UTC datetime.
    
    Returns:
        datetime: Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


class Task(Base):
    """Task model for storing task information."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    datetime_to_do: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    task_info: Mapped[str] = mapped_column(String(1024))
