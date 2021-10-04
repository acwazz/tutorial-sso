import fastapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from .database import Database
from .config import APP_VERSION, DEBUG
from .utils.response import DJSONResponse
from .utils.exceptions import WebException, web_exception_handler, starlette_http_exception_handler, validation_exception_handler
from .web_services import router



tags_metadata = [
    {
        "name": "Info",
        "description": "Servizi informativi",
    },
    {
        "name": "Authentication Services",
        "description": "Servizi per l'autenticazione",
    },
    {
        "name": "Admin",
        "description": "Drop e creazione di nuove API Keys",
    },
    {
        "name": "User Services",
        "description": "Servizi per la gestione della repo utenti",
    }
]


app = fastapi.FastAPI(
    debug=DEBUG,
    version = APP_VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/",
    redoc_url="/redoc",
    title="LemonSSO 🍋",
    description="Servizio SSO tutorial Python",
    openapi_tags=tags_metadata,
    default_response_class=DJSONResponse
)
app.add_event_handler("startup", Database.connect)
app.add_event_handler("shutdown", Database.disconnect)

app.add_exception_handler(WebException, web_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(fastapi.exceptions.RequestValidationError, validation_exception_handler)

app.include_router(router)