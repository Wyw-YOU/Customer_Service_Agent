from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, chat, order, product, user
from app.config.database import close_db, init_db
from app.config.settings import settings
from app.middleware.logging import ExceptionMiddleware, LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="AI Digital Mall Customer Service Agent",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(ExceptionMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
