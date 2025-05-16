from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    """Base schema for Task"""
    datetime_to_do: datetime
    task_info: str


class TaskCreate(TaskBase):
    """Schema for creating a Task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a Task"""
    datetime_to_do: datetime | None = None
    task_info: str | None = None


class Task(TaskBase):
    """Schema for reading a Task (includes fields from DB like id, created_at, updated_at)"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
