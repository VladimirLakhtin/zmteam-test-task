from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from .base import BaseCRUD


class TaskCRUD(BaseCRUD[Task, TaskCreate, TaskUpdate]):
    model = Task
