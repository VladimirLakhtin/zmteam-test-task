"""Task CRUD operations module."""

from app.crud.base import BaseCRUD
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskCRUD(BaseCRUD[Task, TaskCreate, TaskUpdate]):
    """CRUD operations handler for Task model.
    
    Attributes:
        model (Task): The SQLAlchemy model class for Task
    """
    model = Task
