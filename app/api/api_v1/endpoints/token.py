from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.token_schema import Token, User
from app.api.auth import auth_jwt
from app.api.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.dbcontext.db_token import token_dbcontext
from app.handlers import exception_handler, log_database_handler

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logdb = log_database_handler.LogDBHandler()
logger.addHandler(logdb)

router = APIRouter(route_class=exception_handler.ValidationErrorLoggingRoute)

security = HTTPBasic()

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    
    try:
        logger.info("token API call start...")
        _obj_token_dbcontext = token_dbcontext()
        ds = _obj_token_dbcontext.get_api_consumer_details(form_data.username)

        if ds is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        is_password_valid = auth_jwt.verify_password(form_data.password, ds[0]['hashed_password'])

        if is_password_valid == False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # access_token = auth_jwt.create_access_token(
        #     data={"sub": ds[0]['user_name'],"client_id": ds[0]['client_id']}, expires_delta=access_token_expires
        # )
        access_token = auth_jwt.create_access_token(
            data=ds, expires_delta=access_token_expires
        )
        logger.info("token API call end...")
        Token.access_token = access_token
        Token.token_type = "bearer"
        return Token
    
    except Exception as ex:
        raise ex
    
@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(auth_jwt.get_current_active_user)]
):
    return current_user

# Using Custom JWT Bearer from auth_bearer
@router.get("/users/me/items/", dependencies=[Depends(JWTBearer())])
async def read_own_items():
    return [{"item_id": "Foo", "owner": "current_user"}]