import typing
from dynaconf import settings
from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask


class DJSONResponse(ORJSONResponse):
    media_type = "application/json; charset=utf-8"
    body_meta_code = "OK"
    body_meta_message = "Operation Done"

    def __init__(
            self, content: typing.Any = None, body_meta_code: str = None, body_meta_message: str = None, body_meta_extra: dict = None,
            status_code: int = 200, headers: dict = None, background: BackgroundTask = None) -> None:
        if body_meta_code is not None:
            self.body_meta_code = body_meta_code
        if body_meta_message is not None:
            self.body_meta_message = body_meta_message
        self.body_meta_extra = body_meta_extra or {}
        super().__init__(content=content, status_code=status_code, headers=headers, background=background)

    @property
    def body_metadata(self):
        return {
            "error": self.status_code >= 400,
            "version": settings.get("YAB_APP_VERSION"),
            "code": self.body_meta_code,
            "message": self.body_meta_message
        }

    def wrap_content(self, content: typing.Any) -> dict:
        out = {
            "meta": dict(**self.body_metadata, **self.body_meta_extra) if self.body_meta_extra else self.body_metadata,
        }
        if self.status_code >= 400:
            out['reason'] = content
        else:
            out['data'] = content
        return out

    def render(self, content: typing.Any) -> bytes:
        return super().render(self.wrap_content(content))

