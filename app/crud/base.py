from abc import abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    @property
    @abstractmethod
    def model(self):
        raise NotImplemented

    async def get(
            self,
            db: AsyncSession,
            id: Any,
    ) -> Optional[ModelType]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.id == id)
        )
        return result.scalars().first()

    async def get_many(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
    ) -> List[ModelType]:
        result = await db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
            self,
            db: AsyncSession,
            obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        if not create_data:
            return None

        db_obj = self.model(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db: AsyncSession,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if not update_data:
            return db_obj

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        await db.execute(
            sqlalchemy_update(self.model).
            where(self.model.id == db_obj.id).
            values(**update_data)
        )
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
            self,
            db: AsyncSession,
            id: int,
    ) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if obj:
            await db.execute(
                sqlalchemy_delete(self.model)
                .where(self.model.id == id)
            )
            await db.commit()
        return obj
