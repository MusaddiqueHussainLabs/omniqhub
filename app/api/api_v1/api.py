from fastapi import APIRouter
from app.api.api_v1.endpoints import sample ,token, conversations, ws_connect, documents

api_router = APIRouter()

api_router.include_router(sample.router)
api_router.include_router(token.router)
api_router.include_router(conversations.router)
api_router.include_router(ws_connect.router)
api_router.include_router(documents.router)