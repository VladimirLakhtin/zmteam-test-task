from datetime import datetime, timezone, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import TaskCRUD
from app.infrastructure.config import settings

PREFIX = settings.api_prefix.api + settings.api_prefix.tasks
task_crud = TaskCRUD()


@pytest.mark.parametrize(
    "task_data, status_code",
    [
        [
            {
                "datetime_to_do": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                "task_info": "Test task info from API test",
            },
            status.HTTP_201_CREATED,
        ],
        [
            {
                "datetime_to_do": "not-a-datetime",
                "task_info": "Test task with invalid datetime"
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ],
        [
            {
                "task_info": "Test task info from API test",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ],
    ]
)
@pytest.mark.asyncio
async def test_create_task(
        async_client: AsyncClient, db_session: AsyncSession,
        task_data, status_code,
):
    response = await async_client.post(f"{PREFIX}/create", json=task_data)
    assert response.status_code == status_code
    if status_code != status.HTTP_201_CREATED:
        return

    created_task = response.json()
    assert created_task["task_info"] == task_data["task_info"]
    expected_fields = {
        "id",
        "created_at",
        "updated_at",
        "task_info",
        "datetime_to_do",
    }
    assert set(created_task.keys()) == expected_fields
    assert created_task["datetime_to_do"] is not None

    db_task_obj = await task_crud.get(db=db_session, id=created_task["id"])
    assert db_task_obj is not None
    assert db_task_obj.task_info == task_data["task_info"]


@pytest.mark.asyncio
async def test_get_task_list(
        async_client: AsyncClient, test_tasks: list[dict],
):
    response = await async_client.get(f"{PREFIX}/list")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["task_info"] == test_tasks[0]["task_info"]
    assert tasks[1]["task_info"] == test_tasks[1]["task_info"]


@pytest.mark.parametrize(
    "task_id, status_code",
    [
        [1, status.HTTP_200_OK],
        [3, status.HTTP_404_NOT_FOUND],
    ]
)
@pytest.mark.asyncio
async def test_get_single_task(
        async_client: AsyncClient, test_tasks: list[dict],
        task_id, status_code,
):
    response = await async_client.get(f"{PREFIX}/{task_id}")

    assert response.status_code == status_code
    if status_code != status.HTTP_200_OK:
        return

    fetched_task = response.json()
    assert fetched_task["id"] == task_id
    assert fetched_task["task_info"] == test_tasks[task_id - 1]["task_info"]


@pytest.mark.parametrize(
    "task_id, update_data, status_code",
    [
        [1, {"task_info": "New task info"}, status.HTTP_200_OK],
        [3, {"task_info": "New task info"}, status.HTTP_404_NOT_FOUND],
    ]
)
@pytest.mark.asyncio
async def test_update_task(
        async_client: AsyncClient, test_tasks: list[dict],
        task_id, update_data, status_code
):
    response = await async_client.patch(f"{PREFIX}/{task_id}/update", json=update_data)

    assert response.status_code == status_code
    if status_code != status.HTTP_200_OK:
        return

    updated_task_response = response.json()
    assert updated_task_response["id"] == task_id
    assert updated_task_response["task_info"] == update_data["task_info"]


@pytest.mark.parametrize(
    "task_id, status_code",
    [
        [1, status.HTTP_200_OK],
        [3, status.HTTP_404_NOT_FOUND],
    ]
)
@pytest.mark.asyncio
async def test_delete_task(
        async_client: AsyncClient, test_tasks: list[dict],
        task_id, status_code,
):
    response = await async_client.delete(f"{PREFIX}/{task_id}")

    assert response.status_code == status_code
    if status_code != status.HTTP_200_OK:
        return

    deleted_task_response = response.json()
    assert deleted_task_response["id"] == task_id

    get_response = await async_client.get(f"{PREFIX}/{task_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
