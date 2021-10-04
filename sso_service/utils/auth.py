from fastapi import Depends
from fastapi.security import APIKeyHeader
from .exceptions import Forbidden
from ..config import ADMIN_APIKEY
from ..models import RegisteredService, registered_service_repo


ADMIN_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", scheme_name="Admin API Key")

def check_api_key_admin(auth: str = Depends(ADMIN_API_KEY_HEADER)) -> bool:
    if auth != ADMIN_APIKEY:
        raise Forbidden("Action not permitted")
    return True


SERVICE_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", scheme_name="Service API Key")

async def check_api_key(auth: str = Depends(SERVICE_API_KEY_HEADER)) -> RegisteredService:
    inst = await registered_service_repo.retrieve_by_api_key(auth)
    if not inst:
        raise Forbidden("Action not permitted")
    return inst




