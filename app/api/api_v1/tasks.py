"""Task management API endpoints module."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import TaskCRUD
from app.dependencies import get_db_session, get_task_crud
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
    db_task = await task_crud.create(db=db, obj_in=task_payload)
    return db_task


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
    tasks_list = await task_crud.get_many(db, skip=skip, limit=limit)
    return tasks_list


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
    db_task = await task_crud.get(db, id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


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
    db_task_to_update = await task_crud.get(db, id=task_id)
    if not db_task_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    updated_task = await task_crud.update(db=db, db_obj=db_task_to_update, obj_in=task_payload)
    return updated_task


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
    deleted_task = await task_crud.delete(db=db, id=task_id)
    if deleted_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return deleted_task
