from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.interactions import router
from app.core import get_settings
from app.db.session import Base, engine
from app.models import interaction

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
