import os

# Overriding Dynaconf settings
os.environ['SETTINGS_FILE_FOR_DYNACONF'] = '["settings.toml", "secrets.toml"]'
os.environ['ENVVAR_PREFIX_FOR_DYNACONF'] = "false"
from dynaconf import settings

# Getting Env Vars
SERVER_BINDS = str(settings.get("SERVER_BINDS", "localhost:8000")).split(";")
LOGLEVEL = settings.get("SERVER_LOGLEVEL", "info")


bind = SERVER_BINDS
loglevel = LOGLEVEL
errorlog = "-"
workers = 1
use_reloader = True
websocket_ping_interval = 20