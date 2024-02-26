import secrets
import pandas as pd
from typing import Callable, Annotated, Union

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, WebSocketException, APIRouter, Depends, Query, HTTPException, status, Request, Body, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta, timezone

from app.schemas.token_schema import AccessTokenSchema, TokenRequestBodyPayload, TokenClaim
from app.schemas.conversations_schema import Conversations
from app.api.auth import auth_jwt
from app.api.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.dbcontext.db_token import token_dbcontext
from app.handlers import exception_handler, log_database_handler
from app.models.constants import constants
from app.services.ws_connection_manager import ws_connection_manager

import logging
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logdb = log_database_handler.LogDBHandler()
logger.addHandler(logdb)

router = APIRouter(route_class=exception_handler.ValidationErrorLoggingRoute)

security = HTTPBasic()

async def get_token_param(
    t: Annotated[str | None, Query()] = None
):
    if t is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return t

async def get_connectionId_param(
    connectionId: Annotated[str | None, Query()] = None,
):
    if connectionId is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return connectionId

@router.websocket("/directline/conversations/{conversationId}/stream")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    conversationId: str,
    watermark: Annotated[str | None, Query()] = None,
    connectionId: Annotated[str, Depends(get_connectionId_param)],
    t: Annotated[str, Depends(get_token_param)]
):

    try:
        await ws_connection_manager.connect(websocket)
        while True:
            data = await websocket.receive_json()
            await websocket.send_json(data)
            # await websocket.send_text(f"Message text was: {data} " + conversationId + watermark + connectionId + t)

    except WebSocketDisconnect:
        ws_connection_manager.disconnect(websocket)

    except Exception as ex:
        raise ex