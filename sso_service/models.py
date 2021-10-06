import datetime
import secrets
from typing import Optional
from odmantic import Model, Field, EmbeddedModel
from odmantic.query import QueryExpression
from pydantic import SecretStr
from .database import BaseRepository
from .utils.exceptions import NotFound, Conflict
from .config import password_context


class NotUnique(Conflict):
    default_message = "Field value is not unique"


def generate_token_value():
    return secrets.token_urlsafe(128)


class UserToken(EmbeddedModel):
    access_value: str = Field(default_factory=generate_token_value)
    refresh_value: str = Field(default_factory=generate_token_value)
    access_lifetime: float = datetime.timedelta(hours=10).total_seconds()
    refresh_lifetime: float = datetime.timedelta(hours=10, minutes=30).total_seconds()
    is_valid: bool
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    def is_valid_access_token(self):
        eol = self.created + datetime.timedelta(seconds=self.access_lifetime)
        return datetime.datetime.utcnow() <= eol and self.is_valid
    
    def is_valid_refresh_token(self):
        eol = self.created + datetime.timedelta(seconds=self.refresh_lifetime)
        return datetime.datetime.utcnow() <= eol


class User(Model):
    username: str
    password: str
    token: Optional[UserToken]
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        parse_doc_with_default_factories = True
        collection = "users"


class UserRepository(BaseRepository):
    model = User

    async def sign_up(self, username: str, password: SecretStr):
        exists = await self.db.engine.find_one(self.model, self.model.username == username)
        if exists:
            raise NotUnique("Username is not unique")
        pwd = password_context.hash(password.get_secret_value().encode("utf-8"))
        return await self.insert({"username": username, "password": pwd})

    async def partial_update(self, instance: Model, data: dict) -> Optional[Model]:
        if username := data.get('username'):
            exists = await self.db.engine.find_one(self.model, self.model.username == username)
            if exists and exists.id != instance.id:
                raise NotUnique("Username is not unique")
        if passw := data.get('password'):
            data['password'] = password_context.hash(passw.encode("utf-8"))
        return await super().partial_update(instance, data)

    async def retrive_by_username(self, username: str) -> User:
        inst = await self.db.engine.find_one(self.model, self.model.username == username)
        if not inst:
            raise NotFound("User not found.")
        return inst

    async def retrieve_by_access_token(self, access_token: str) -> User:
        inst = await self.db.engine.find_one(self.model, {'token.access_value': {"$eq": access_token}})
        if not inst:
            raise NotFound("User not found.")
        return inst
    
    async def retrieve_by_refresh_token(self, refresh_token: str) -> User:
        inst = await self.db.engine.find_one(self.model, {'token.refresh_value': {"$eq": refresh_token}})
        if not inst:
            raise NotFound("User not found.")
        return inst
    
    async def invalidate_token(self, user: User) -> User:
        user.token.is_valid = False
        return await self.db.engine.save(user)

user_repo = UserRepository()


class RegisteredService(Model):
    name: str
    api_key: str = Field(default_factory=generate_token_value)
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    class Config:
        parse_doc_with_default_factories = True
        collection = "registeredServices"


class RegisteredServiceRepo(BaseRepository):
    model = RegisteredService

    async def retrieve_by_api_key(self, api_key: str) -> Optional[RegisteredService]:
        return await self.db.engine.find_one(self.model, self.model.api_key == api_key)

registered_service_repo = RegisteredServiceRepo()