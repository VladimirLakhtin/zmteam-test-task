"""Task CRUD operations module."""

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from .base import BaseCRUD


class TaskCRUD(BaseCRUD[Task, TaskCreate, TaskUpdate]):
    """CRUD operations handler for Task model.
    
    Attributes:
        model (Task): The SQLAlchemy model class for Task
    """
    model = Task
