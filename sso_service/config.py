from dynaconf import settings
from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

APP_VERSION = "1.2.4"
settings['APP_VERSION'] = APP_VERSION
DEBUG = settings.get("DEBUG", False)
MONGO_URL = settings.get("MONGO_URL", "mongodb://localhost:27017/lemonSSO")
MONGO_DATABASE = settings.get("MONGO_DATABASE", "lemonSSO")
ADMIN_APIKEY = settings.get("ADMIN_APIKEY", "test_api_key")
