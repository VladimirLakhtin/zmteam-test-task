"""Base CRUD operations module."""

from abc import abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.exeptions import CRUDException, CreateError, NotFoundError, DeleteError, UpdateError
from app.infrastructure.logger import logger
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations.
    
    This class provides generic CRUD operations that can be used with any
    SQLAlchemy model. It uses type variables to ensure type safety across
    different models and their corresponding Pydantic schemas.
    
    Type Variables:
        ModelType: SQLAlchemy model class
        CreateSchemaType: Pydantic model for creation
        UpdateSchemaType: Pydantic model for updates
    """

    @property
    @abstractmethod
    def model(self):
        """Abstract property that must be implemented by child classes.
        
        Returns:
            The SQLAlchemy model class for this CRUD operations handler.
            
        Raises:
            NotImplementedError: If not implemented by child class
        """
        raise NotImplemented

    async def get(
            self,
            db: AsyncSession,
            id: Any,
    ) -> Optional[ModelType]:
        """Retrieve a single record by ID.

        Args:
            db (AsyncSession): Database session
            id (Any): Record ID to retrieve

        Returns:
            Optional[ModelType]: Retrieved record or None if not found
        """
        logger.debug(f"Fetching {self.model.__name__} with ID={id}")
        try:
            result = await db.execute(select(self.model).filter(self.model.id == id))
            instance = result.scalars().first()
            if not instance:
                logger.warning(f"{self.model.__name__} with ID={id} not found")
            return instance
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching {self.model.__name__} with ID={id}")
            raise CRUDException from e

    async def get_many(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
    ) -> List[ModelType]:
        """Retrieve multiple records with pagination.

        Args:
            db (AsyncSession): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[ModelType]: List of retrieved records
        """
        logger.debug(f"Fetching many {self.model.__name__} (skip={skip}, limit={limit})")
        try:
            result = await db.execute(
                select(self.model).offset(skip).limit(limit)
            )
            items = result.scalars().all()
            logger.info(f"Fetched {len(items)} {self.model.__name__}(s)")
            return items
        except SQLAlchemyError as e:
            logger.exception(f"Error fetching list of {self.model.__name__}")
            raise CRUDException from e

    async def create(
            self,
            db: AsyncSession,
            obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new record.

        Args:
            db (AsyncSession): Database session
            obj_in (Union[CreateSchemaType, Dict[str, Any]]): Data for new record

        Returns:
            ModelType: Created record

        Note:
            Returns None if no data is provided for creation
        """
        logger.debug(f"Creating new {self.model.__name__}")
        try:
            create_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            if not create_data:
                logger.warning("Create failed: no input data")
                raise CreateError("No data provided for creation")

            db_obj = self.model(**create_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)

            logger.info(f"Created {self.model.__name__} with ID={db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(f"Error creating {self.model.__name__}")
            raise CreateError from e

    async def update(
            self,
            db: AsyncSession,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record.

        Args:
            db (AsyncSession): Database session
            db_obj (ModelType): Existing record to update
            obj_in (Union[UpdateSchemaType, Dict[str, Any]]): Update data

        Returns:
            ModelType: Updated record

        Note:
            Returns original object if no update data is provided
        """
        logger.debug(f"Updating {self.model.__name__} ID={db_obj.id}")
        try:
            update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

            if not update_data:
                logger.info("Update skipped: no fields to update")
                return db_obj

            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])

            await db.execute(
                sqlalchemy_update(self.model)
                .where(self.model.id == db_obj.id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(db_obj)

            logger.info(f"Updated {self.model.__name__} ID={db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(f"Error updating {self.model.__name__} ID={db_obj.id}")
            raise UpdateError from e

    async def delete(
            self,
            db: AsyncSession,
            id: int,
    ) -> Optional[ModelType]:
        """Delete a record by ID.

        Args:
            db (AsyncSession): Database session
            id (int): ID of record to delete

        Returns:
            Optional[ModelType]: Deleted record or None if not found
        """
        logger.debug(f"Deleting {self.model.__name__} ID={id}")
        try:
            obj = await self.get(db, id=id)
            if not obj:
                logger.warning(f"Delete failed: {self.model.__name__} ID={id} not found")
                raise NotFoundError(f"{self.model.__name__} with ID {id} not found")

            await db.execute(sqlalchemy_delete(self.model).where(self.model.id == id))
            await db.commit()

            logger.info(f"Deleted {self.model.__name__} ID={id}")
            return obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(f"Error deleting {self.model.__name__} ID={id}")
            raise DeleteError from e
