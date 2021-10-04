from .models import user_repo, UserToken
from .utils.exceptions import Unauthorized, Forbidden
from .config import password_context


async def renew_auth(user):
    auth = UserToken(is_valid=True)
    return await user_repo.partial_update(user, data={"token": auth})


async def drop_auth(user):
    user.token = None
    await user_repo.db.engine.save(user)


async def signout(token: str):
    user = await user_repo.retrieve_by_access_token(token)
    await drop_auth(user)
    return True


async def verify(access_token: str):
    try:
        user = await user_repo.retrieve_by_access_token(access_token)
        if not user.token.is_valid_access_token():
            await user_repo.invalidate_token(user)
            raise Exception("Token expired or not valid.")
        return user
    except Exception as e:
        raise Forbidden(str(e))


async def signin(username: str, password: str):
    try:
        user = await user_repo.retrive_by_username(username)
        verify = password_context.verify(secret=password.get_secret_value().encode("utf-8"), hash=user.password.encode("utf-8"))
        if not verify:
            raise Exception()
        if not user.token or not user.token.is_valid_access_token():
            user = await renew_auth(user)
        return {
            "user": user,
            "auth": {
                "token": user.token.access_value,
                "refresh": user.token.refresh_value
            }
        }
    except Exception:
        raise Unauthorized("Wrong credentials")


async def refresh(refresh_token: str):
    try:
        user = await user_repo.retrieve_by_refresh_token(refresh_token)
        if not user.token.is_valid_refresh_token():
            await drop_auth(user)
            raise Exception()
        user = await renew_auth(user)
        return {
            "user": user,
            "auth": {
                "token": user.token.access_value,
                "refresh": user.token.refresh_value
            }
        }
    except Exception:
        raise Unauthorized("Token is not valid")


