import secrets
import pandas as pd
from typing import Callable, Annotated, Union

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Body, Response, UploadFile, File
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

class UploadDocumentsResponse:
    def __init__(self, UploadedFiles, Error=None):
        self.UploadedFiles = UploadedFiles
        self.Error = Error

    @property
    def IsSuccessful(self):
        return self.Error is None and len(self.UploadedFiles) > 0

    @staticmethod
    def FromError(error):
        return UploadDocumentsResponse([], error)


@router.post("/uploadfiles")
async def create_upload_files(files: list[UploadFile] = File(...)):
    try:
        filenames = [file.filename for file in files]
        response = UploadDocumentsResponse(UploadedFiles=filenames)
        return response
    except Exception as e:
        error_response = UploadDocumentsResponse.FromError(str(e))
        return error_response


from datetime import datetime
from pydantic import BaseModel, HttpUrl
from enum import Enum

class DocumentProcessingStatus(Enum):
    NotProcessed = 0
    Succeeded = 1
    Failed = 2

class EmbeddingType(Enum):
    AzureSearch = 0
    Pinecone = 1
    Qdrant = 2
    Milvus = 3

class DocumentResponse(BaseModel):
    Name: str
    ContentType: str
    Size: int
    LastModified: datetime
    Url: HttpUrl
    Status: DocumentProcessingStatus
    EmbeddingType: EmbeddingType

@router.get("/documents", response_model=DocumentResponse)
async def upload_document():
    return DocumentResponse(
        Name="document.pdf",
        ContentType="application/pdf",
        Size=1024,
        LastModified=datetime.now(),
        Url="https://example.com/document.pdf",  # Replace with the actual URL
        Status=DocumentProcessingStatus.Succeeded,
        EmbeddingType=EmbeddingType.AzureSearch
    )