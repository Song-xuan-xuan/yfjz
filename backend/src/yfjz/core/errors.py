from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(ValueError):
    pass


class ValidationAppError(ValueError):
    pass


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValidationAppError)
    async def validation_handler(_: Request, exc: ValidationAppError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
