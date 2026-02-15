from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from svc.routes import wallets


def create_app() -> FastAPI:
    """
    Создает и настраивает FastAPI приложение.

    Returns:
        Настроенное FastAPI приложение с подключенными роутами и CORS middleware.
    """
    app = FastAPI(
        title="Wallets API",
        version="1.0.0",
        debug=True
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Роуты
    app.include_router(wallets.router)
    return app


app = create_app()
