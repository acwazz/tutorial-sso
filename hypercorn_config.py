import os
import multiprocessing

# Overriding Dynaconf settings
os.environ['SETTINGS_FILE_FOR_DYNACONF'] = '["settings.toml", "secrets.toml"]'
os.environ['ENVVAR_PREFIX_FOR_DYNACONF'] = "false"
from dynaconf import settings

# Getting Env Vars
SERVER_BINDS = str(settings.get("SERVER_BINDS", "localhost:8000")).split(";")
LOGLEVEL = settings.get("SERVER_LOGLEVEL", "info")
WORKERS = settings.get("SERVER_WORKERS_NUM", (multiprocessing.cpu_count() * 2) + 1)


bind = SERVER_BINDS
loglevel = LOGLEVEL
errorlog = "-"
workers = WORKERS
websocket_ping_interval = 20