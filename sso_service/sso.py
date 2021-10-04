import datetime
from .models import user_repo, UserToken
from .utils.exceptions import Unauthorized, Forbidden
from .config import password_context


async def signout(token: str):
    user = await user_repo.retrieve_by_access_token(token)
    user.token = None
    await user_repo.db.engine.save(user)
    return True


async def signin(username: str, password: str):
    try:
        user = await user_repo.retrive_by_username(username)
        verify = password_context.verify(secret=password.get_secret_value().encode("utf-8"), hash=user.password.encode("utf-8"))
        if not verify:
            raise Exception()
        auth = UserToken(is_valid=True)
        updated_user = await user_repo.partial_update(user, data={"token": auth})
        return {
            "user": updated_user,
            "auth": {
                "token": auth.access_value,
                "refresh": auth.refresh_value
            }
        }
    except Exception as e:
        raise Unauthorized("Wrong credentials")


async def refresh(refresh_token: str):
    try:
        user = await user_repo.retrieve_by_refresh_token(refresh_token)
        refresh_eol = user.token.created + datetime.timedelta(seconds=user.token.refresh_lifetime)
        if datetime.datetime.now() >= refresh_eol:
            raise Exception()
        auth = UserToken(is_valid=True)
        updated_user = await user_repo.partial_update(user, data={"token": auth})
        return {
            "user": updated_user,
            "auth": {
                "token": auth.access_value,
                "refresh": auth.refresh_value
            }
        }
    except Exception:
        raise Unauthorized("Wrong credentials")


async def verify(access_token: str):
    try:
        user = await user_repo.retrieve_by_access_token(access_token)
        access_eol = user.token.created + datetime.timedelta(seconds=user.token.access_lifetime)
        if datetime.datetime.now() >= access_eol:
            raise Exception()
        return user
    except Exception:
        raise Forbidden("Wrong credentials")