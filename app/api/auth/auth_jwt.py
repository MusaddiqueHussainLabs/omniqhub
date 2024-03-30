from datetime import datetime, timedelta, timezone
from typing import Any, Union, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.schemas.token_schema import User, TokenData, TokenClaim
from app.dbcontext.db_token import token_dbcontext
from app.core.config import settings
from app.models.constants import constants
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        
        username: str = decoded_token.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.TOKEN_INVALID_CREDENTIALS)
        else:
            return decoded_token
    except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.TOKEN_EXPIRED)
    except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.TOKEN_INVALID)

def get_user(username: str):

    _obj_token_dbcontext = token_dbcontext()
    ds = _obj_token_dbcontext.get_api_consumer_details(username)

    if ds is None:
        return None
    
    User.username = str(ds[0]['user_name'])
    User.full_name = str(ds[0]['full_name'])
    User.email = str(ds[0]['email'])
    User.disabled = bool(ds[0]['disabled'])

    return User
    
# def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire, "iss": str(settings.ISSUER)})

#     # add few more claims if required
#     # to_encode = {"exp": expire, "sub": str(subject), "tid": str(settings.TID), 
#     #             "appid": str(accountid), "clientid": str(clientid), "scp": str(scope), 
#     #             "issuer": str(settings.ISSUER)}
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

def create_access_token(data: list, expires_delta: Union[timedelta, None] = None):
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = TokenClaim(client_id= str(data[0]['client_id']),
                           sub=str(data[0]['user_name']),
                           iss=str(settings.ISSUER),
                           exp=int(expire.timestamp()))

    # add few more claims if required
    # to_encode = {"exp": expire, "sub": str(subject), "tid": str(settings.TID), 
    #             "appid": str(accountid), "clientid": str(clientid), "scp": str(scope), 
    #             "issuer": str(settings.ISSUER)}
    encoded_jwt = jwt.encode(to_encode.model_dump(), settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=constants.TOKEN_INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.TOKEN_EXPIRED)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=constants.TOKEN_INACTIVE_USER)
    return current_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_claims(token: Annotated[str, Depends(oauth2_scheme)]):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=constants.TOKEN_INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload is None:
            raise credentials_exception

        TokenClaim.client_id = payload.get("client_id")
        TokenClaim.sub = payload.get("sub")
        TokenClaim.exp = payload.get("exp")
        TokenClaim.iss = payload.get("iss")

    except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.TOKEN_EXPIRED)
    except JWTError:
        raise credentials_exception
    
    return TokenClaim

async def get_current_token_claims(
    current_claims: Annotated[TokenClaim, Depends(get_current_claims)]
):
    
    return current_claims