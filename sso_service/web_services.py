from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from .utils.auth import check_api_key, check_api_key_admin
from .utils.exceptions import NotFound, Forbidden
from .models import RegisteredService, registered_service_repo, user_repo
from .serializers import WriteRegisterdService, ReadUser, WriteUser, AuthenticatedUser, Credentials, UpdateUser
from sso_service import sso

router = APIRouter(prefix="/api/v1")


@router.get("/echo/", response_model=dict, name="Echo Service", tags=["Info"])
def echo_service():
    """
    Se consumato ritorna una risposta in caso il backend sia in uptime.
    """
    return {"message": "Everything works fine! 🚀", "origin": "sso-service"}


@router.post("/registerd-services", status_code=201, response_model=RegisteredService, tags=["Admin"])
async def create_registered_service(service: WriteRegisterdService, auth: bool = Depends(check_api_key_admin)):
    """Crea una nuova api key per l'integrazione"""
    instance = await registered_service_repo.insert(service.dict())
    return instance


@router.get("/registered-services", response_model=List[RegisteredService], tags=["Admin"])
async def list_registered_services(auth: bool = Depends(check_api_key_admin)):
    """Ritorna la lista di tutti i servizi integrati"""
    collection = await registered_service_repo.list()
    return collection


class OperationExit(BaseModel):
    operation: bool


@router.delete("/registered-services/{registered_service_id}", response_model=OperationExit, tags=["Admin"])
async def delete_registered_service(registered_service_id: str, auth: bool = Depends(check_api_key_admin)):
    """elimina l'account di un servizio di integrazione"""
    await registered_service_repo.destroy(registered_service_id)
    return {"operation": True}


@router.post("/users/", status_code=201, response_model=ReadUser, tags=["User Services"])
async def create_user(user: WriteUser, service: RegisteredService = Depends(check_api_key)):
    """Crea un nuovo utente"""
    instance = await user_repo.sign_up(**user.dict())
    return instance.dict()


@router.get("/users/", response_model=List[ReadUser], tags=["User Services"])
async def list_users(service: RegisteredService = Depends(check_api_key)):
    """Ritorna la lista degli utenti"""
    collection = await user_repo.list()
    return list(map(lambda u: u.dict(), collection))


@router.put("/users/{user_id}", response_model=ReadUser, tags=["User Services"])
async def update_user(user_id: str, payload: UpdateUser, service: RegisteredService = Depends(check_api_key)):
    """Modifica un utente"""
    inst = await user_repo.retrieve(user_id)
    if not inst:
        raise NotFound("User not found")
    updated = await user_repo.partial_update(inst, data={
        "username": payload.username, 
        "password": payload.password.get_secret_value() if payload.password else None
    })
    return updated


@router.delete("/users/{user_id}", response_model=OperationExit, tags=["User Services"])
async def delete_user(user_id: str, service: RegisteredService = Depends(check_api_key)):
    """Elimina un utente"""
    await user_repo.destroy(user_id)
    return {"operation": True}


@router.get("/users/{user_id}", response_model=ReadUser, tags=["User Services"])
async def retrieve_user(user_id: str, service: RegisteredService = Depends(check_api_key)):
    """Elimina un utente"""
    inst = await user_repo.retrieve(user_id)
    if not inst:
        raise NotFound("User not found")
    return inst


@router.post("/auth/signin", response_model=AuthenticatedUser, tags=["Authentication Services"])
async def sign_in(credentials: Credentials, service: RegisteredService = Depends(check_api_key)):
    return await sso.signin(**credentials.dict())


class AuthTokenReq(BaseModel):
    access_token: str


@router.post("/auth/signout", response_model=OperationExit, tags=["Authentication Services"])
async def sign_out(req: AuthTokenReq, service: RegisteredService = Depends(check_api_key)):
    signout = await sso.signout(req.access_token)
    return {"operation": signout}


@router.post("/auth/verify", response_model=OperationExit, tags=["Authentication Services"])
async def verify(req: AuthTokenReq, service: RegisteredService = Depends(check_api_key)):
    try:
        await sso.verify(req.access_token)
        return {"operation": True}
    except Forbidden:
        return {"operation": False}


@router.post("/auth/sso", response_model=ReadUser, tags=["Authentication Services"])
async def single_sign_on(req: AuthTokenReq, service: RegisteredService = Depends(check_api_key)):
    return await sso.verify(req.access_token)


class RefreshReq(BaseModel):
    refresh_token: str


@router.post("/auth/refresh", response_model=AuthenticatedUser, tags=["Authentication Services"])
async def refresh(refresh: RefreshReq, service: RegisteredService = Depends(check_api_key)):
    inst = await sso.refresh(refresh.refresh_token)
    return inst