import secrets
import pandas as pd
from typing import Callable, Annotated, Union

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Body, Response
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

import logging
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logdb = log_database_handler.LogDBHandler()
logger.addHandler(logdb)

router = APIRouter(route_class=exception_handler.ValidationErrorLoggingRoute)

security = HTTPBasic()

@router.post("/directline/conversations", response_model=Conversations)
async def create_conversations(
    current_claims: Annotated[TokenClaim, Depends(auth_jwt.get_current_token_claims)]
):

    try:
        logger.info("conversations API call start...")

        _obj_token_dbcontext = token_dbcontext()
        ds = _obj_token_dbcontext.get_api_consumer_details(current_claims.sub)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_jwt.create_access_token(
            data=ds, expires_delta=access_token_expires
        )
        expire = datetime.now(timezone.utc) + access_token_expires
        streamUrl = settings.STREAM_BASE_URL

        conv = Conversations(access_token=str(access_token),
                             conversationId=str(uuid.uuid4()),
                             expires_in=int(expire.timestamp()),
                             streamUrl=str(streamUrl))
        
        logger.info("conversations API call end...")

        return conv
    
    except Exception as ex:
        raise ex