"""Task schema module."""

from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    """Base schema for Task data validation.

    This schema defines the common fields required for all task operations.

    Attributes:
        datetime_to_do (datetime): Scheduled execution time for the task
        task_info (str): Task description or details
    """
    datetime_to_do: datetime
    task_info: str


class TaskCreate(TaskBase):
    """Schema for creating a new Task.
    
    Inherits all fields from TaskBase and is used for task creation requests.
    """
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing Task.
    
    All fields are optional to allow partial updates.
    
    Attributes:
        datetime_to_do (datetime | None): New scheduled execution time
        task_info (str | None): New task description or details
    """
    datetime_to_do: datetime | None = None
    task_info: str | None = None


class Task(TaskBase):
    """Schema for reading Task data.
    
    Includes all base fields plus database-generated fields.
    
    Attributes:
        id (int): Task identifier
        created_at (datetime): Task creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
