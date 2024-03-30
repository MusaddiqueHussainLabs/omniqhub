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

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

from app.schemas.token_schema import AccessTokenSchema, TokenRequestBodyPayload, TokenClaim
from app.schemas.conversations_schema import Conversations
from app.api.auth import auth_jwt
from app.api.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.dbcontext.db_token import token_dbcontext
from app.handlers import exception_handler, log_database_handler
from app.models.constants import constants
from app.services.azure_blob_storage import AzureBlobStorageService

import logging
import uuid
import typing
import os

from dotenv import load_dotenv
load_dotenv(override=True)

connect_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
container_name = os.environ["AZURE_STORAGE_BLOB_CONTAINERS"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logdb = log_database_handler.LogDBHandler()
logger.addHandler(logdb)

router = APIRouter(route_class=exception_handler.ValidationErrorLoggingRoute)

security = HTTPBasic()

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Create the container
container_client = blob_service_client.get_container_client(container_name)

@router.post("/documents")
async def on_post_document_async(files: list[UploadFile] = File(...)):
    try:
        blob_storage = AzureBlobStorageService(blob_service_client=blob_service_client ,container_client=container_client)

        result = await blob_storage.upload_files_async(files=files)

        return result
    
    except Exception as e:
        raise e
    

@router.get("/documents")
async def on_get_documents_async():
    try:
        blob_storage = AzureBlobStorageService(blob_service_client=blob_service_client ,container_client=container_client)
        
        result = await blob_storage.on_get_documents_async()
        
        return result
    except Exception as e:
        raise e