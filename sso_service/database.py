import os
import datetime
from loguru import logger
from typing import Optional
from odmantic import AIOEngine, Model, ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URL, MONGO_DATABASE
from .utils.exceptions import Gone


class Database:
    """Database abstraction Layer (Consider it as a Singleton)"""
    client = None
    engine = None
    log_prefix = f"<> [{os.getpid()}] Server>> "

    @classmethod
    async def connect(cls):
        """Opens connection to Database and instantiates the engine"""
        logger.info(f"{cls.log_prefix}🔌 Connecting to MongoDB...")
        cls.client = AsyncIOMotorClient(MONGO_URL)
        cls.client.is_mongos
        logger.info(f"{cls.log_prefix}✔️  Database connected.")
        cls.init_db_engine()
    
    @classmethod
    async def disconnect(cls):
        """Closes connection to Database"""
        logger.info(f"{cls.log_prefix}🔌 Disconnecting from MongoDB...")
        cls.client.close()
        logger.info(f"{cls.log_prefix}✔️  Database disconnected.")
    
    @classmethod
    def init_db_engine(cls):
        """Initializes the engine"""
        logger.info(f"{cls.log_prefix}⚙️  Initializing MongoDB Engine...")
        cls.engine = AIOEngine(motor_client=cls.client, database=MONGO_DATABASE)
        logger.info(f"{cls.log_prefix}✔️  Engine initialized.")


class BaseRepository:
    """Object implementing the model repository in DB"""
    model: Model = None
    db = Database

    async def partial_update(self, instance: Model, data: dict) -> Optional[Model]:
        """Partially updates a resource

        Args:
            instance (Model): Instance to update
            data (dict): Data

        Returns:
            Optional[Model]: Modified model
        """
        fields = filter(lambda x: x not in ['id', 'updated', 'created'], self.model.__fields__.keys())
        for field in fields:
            if data.get(field, None):
                setattr(instance, field, data[field])
        if hasattr(instance, "updated"):
            instance.updated = datetime.datetime.now()
        return await self.db.engine.save(instance)

    async def retrieve(self, id: str) -> Optional[Model]:
        """Fetch a resource by its ID

        Args:
            id (str): Resource Object ID

        Returns:
            Optional[Model]: The retrieved instance
        """
        query = self.model.id == ObjectId(id)
        return await self.db.engine.find_one(self.model, query)
    
    async def insert(self, data: dict) -> Optional[Model]:
        """Creates or Updates an instance of a model

        Args:
            data (dict): a dictionary describing the model fields and values

        Returns:
            Optional[Model]: The created instance
        """
        inst = self.model(**data)
        return await self.db.engine.save(inst)

    async def retrieve_or_create(self, id: str, defaults: Optional[dict] = None) -> Optional[Model]:
        """Fetch a resource by its ID, if not found creates a new resource

        Args:
            id (str): Resource primary key
            defaults (Optional[dict], optional): Default fields for creation. Defaults to None.

        Returns:
            Optional[Model]: The retrieved or crreated instance
        """
        inst = await self.retrieve(id=id)
        if not inst:
            inst = await self.insert(defaults)
        return inst

    async def destroy(self, id: str) -> Optional[Model]:
        """Deletes a model instance from the repository

        Args:
            id (str): resource ID

        Returns:
            Optional[Model]: The deleted resource
        """
        inst = await self.retrieve(id=id)
        if inst:
            inst = await self.db.engine.delete(inst)
        else:
            raise Gone("Resource gone")
        return inst
    
    async def list(self, *filters):
        """Returns a collection of resources
        Args:
            *filters (tuple): A list of ODMantic compatible filters
        Returns:
            List[Model]: Result of the query
        """
        return await self.db.engine.find(self.model, *filters)
