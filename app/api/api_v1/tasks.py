"""Task management API endpoints module."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.exeptions import CRUDException, NotFoundError
from app.crud.task import TaskCRUD
from app.dependencies import get_db_session, get_task_crud
from app.infrastructure.logger import logger
from app.schemas.task import Task, TaskCreate, TaskUpdate

router = APIRouter(tags=["tasks"])


@router.post("/create", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_new_task_endpoint(
        task_payload: TaskCreate,
        db: AsyncSession = Depends(get_db_session),
        task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Create a new task record in the database.
    
    Args:
        task_payload (TaskCreate): Task creation data including datetime and info
        db (AsyncSession): Database session
        task_crud (TaskCRUD): Task CRUD operations handler
        
    Returns:
        Task: Created task data
        
    Note:
        - datetime_to_do: Expected execution time for the task (UTC recommended)
        - task_info: Information about the task
    """
    try:
        task = await task_crud.create(db=db, obj_in=task_payload)
        logger.info(f"Task created: ID={task.id}")
        return task
    except CRUDException as e:
        logger.exception("Unhandled CRUDException during creation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=List[Task])
async def read_all_tasks_endpoint(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db_session),
        task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Retrieve a list of all tasks with pagination support.
    
    Args:
        skip (int): Number of records to skip (for pagination)
        limit (int): Maximum number of records to return (for pagination)
        db (AsyncSession): Database session
        task_crud (TaskCRUD): Task CRUD operations handler
        
    Returns:
        List[Task]: List of task records
    """
    try:
        tasks = await task_crud.get_many(db=db, skip=skip, limit=limit)
        logger.info(f"Fetched {len(tasks)} tasks")
        return tasks
    except CRUDException as e:
        logger.exception("Failed to fetch tasks")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}", response_model=Task)
async def read_single_task_endpoint(
        task_id: int,
        db: AsyncSession = Depends(get_db_session),
        task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Retrieve data for a specific task by its ID.
    
    Args:
        task_id (int): The ID of the task to retrieve
        db (AsyncSession): Database session
        task_crud (TaskCRUD): Task CRUD operations handler
        
    Returns:
        Task: Task data
        
    Raises:
        HTTPException: If task with given ID is not found
    """
    try:
        task = await task_crud.get(db, id=task_id)
        if not task:
            raise NotFoundError(f"Task with id={task_id} not found")
        logger.info(f"Task fetched: ID={task.id}")
        return task
    except NotFoundError as e:
        logger.warning(f"NotFoundError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except CRUDException as e:
        logger.exception("Failed to fetch task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{task_id}/update", response_model=Task)
async def update_existing_task_endpoint(
        task_id: int,
        task_payload: TaskUpdate,
        db: AsyncSession = Depends(get_db_session),
        task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Update data for an existing task.
    
    Args:
        task_id (int): The ID of the task to update
        task_payload (TaskUpdate): Updated task data
        db (AsyncSession): Database session
        task_crud (TaskCRUD): Task CRUD operations handler
        
    Returns:
        Task: Updated task data
        
    Raises:
        HTTPException: If task with given ID is not found
        
    Note:
        - datetime_to_do (optional): New expected execution time
        - task_info (optional): New task information
    """
    try:
        task = await task_crud.get(db, id=task_id)
        if not task:
            raise NotFoundError(f"Task with id={task_id} not found")
        updated = await task_crud.update(db=db, db_obj=task, obj_in=task_payload)
        logger.info(f"Task updated: ID={updated.id}")
        return updated
    except NotFoundError as e:
        logger.warning(f"NotFoundError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except CRUDException as e:
        logger.exception("Failed to update task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", response_model=Task)
async def delete_task_endpoint(
        task_id: int,
        db: AsyncSession = Depends(get_db_session),
        task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Delete a specific task by its ID.
    
    Args:
        task_id (int): The ID of the task to delete
        db (AsyncSession): Database session
        task_crud (TaskCRUD): Task CRUD operations handler
        
    Returns:
        Task: Deleted task data
        
    Raises:
        HTTPException: If task with given ID is not found
    """
    try:
        deleted = await task_crud.delete(db=db, id=task_id)
        logger.info(f"Task deleted: ID={deleted.id}")
        return deleted
    except NotFoundError as e:
        logger.warning(f"NotFoundError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except CRUDException as e:
        logger.exception("Failed to delete task")
        raise HTTPException(status_code=500, detail="Internal server error")
