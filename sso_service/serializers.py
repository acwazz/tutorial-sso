import datetime
from typing import Optional
from pydantic import BaseModel, SecretStr
from .utils.serializers import PasswordString
from odmantic.bson import BaseBSONModel, ObjectId


class WriteRegisterdService(BaseModel):
    name: str


class WriteUser(BaseModel):
    username: str
    password: PasswordString


class UpdateUser(BaseModel):
    username: Optional[str]
    password: Optional[PasswordString]


class ReadUser(BaseBSONModel):
    id: ObjectId
    username: str
    created: datetime.datetime
    updated: datetime.datetime


class Credentials(BaseModel):
    username: str
    password: SecretStr


class Authentication(BaseModel):
    token: str
    refresh: str


class AuthenticatedUser(BaseBSONModel):
    user: ReadUser
    auth: Authentication
