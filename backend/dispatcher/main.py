from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from dispatcher.api import router

from .core.lifespan import lifespan
from .middleware import APIMiddleware, JWTAuthBackend


def create_app() -> FastAPI:
    app = FastAPI(
        title="Linkding Dispatcher",
        lifespan=lifespan,
    )

    app.include_router(router)
    app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
    app.add_middleware(APIMiddleware)

    return app


app = create_app()
