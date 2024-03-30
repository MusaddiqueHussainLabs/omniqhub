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

from azure.storage.blob import BlobServiceClient

from app.schemas.token_schema import AccessTokenSchema, TokenRequestBodyPayload, TokenClaim
from app.schemas.conversations_schema import Conversations, RequestModel, ResponseModel, ChatResponseModel
from app.api.auth import auth_jwt
from app.api.auth.auth_bearer import JWTBearer
from app.core.config import settings
from app.dbcontext.db_token import token_dbcontext
from app.handlers import exception_handler, log_database_handler
from app.models.constants import constants
from app.models.conversations_response import SupportingContentRecord, SupportingImageRecord, ApproachResponse
from app.services.langchain_service import LangchainService
from app.services.azure_blob_storage import AzureBlobStorageService

import logging
import uuid
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
    
@router.post("/chat-demo", response_model=ResponseModel)
def chat(request: RequestModel):
    dummy_response = ApproachResponse(
        answer="This is a dummy answer. <<What is the deductible?>> <<What is the co-pay?>> [Benefit_Options.pdf]",
        thoughts="These are some dummy thoughts.",
        data_points=[
            SupportingContentRecord(title="Benefit_Options.pdf: Dummy Title 1", content="Benefit_Options.pdf: Dummy Content 1"),
            SupportingContentRecord(title="Benefit_Options.pdf: Dummy Title 2", content="Benefit_Options.pdf: Dummy Content 2"),
        ],
        images=[
            SupportingImageRecord(title="Benefit_Options.pdf: Dummy Image 1", url="http://example.com/image1.jpg"),
            SupportingImageRecord(title="Benefit_Options.pdf: Dummy Image 2", url="http://example.com/image2.jpg"),
        ],
        citation_base_url="http://127.0.0.1:10000/devstoreaccount1/omnihub-container/Benefit_Options.pdf?st=2024-03-23T20%3A13%3A14Z&se=2024-03-23T20%3A43%3A14Z&sp=r&sv=2023-11-03&sr=b&sig=UGES2vmpwllJRpS2Q1JTZj4SxU4BTEd3%2Bzzf7864ejw%3D"
    )

    return ResponseModel(
        answer=dummy_response.answer,
        thoughts=dummy_response.thoughts,
        data_points=dummy_response.data_points,
        images=dummy_response.images,
        citation_base_url=dummy_response.citation_base_url,
        error=dummy_response.error
    )

@router.post("/chat", response_model=ResponseModel)
def chat(request: RequestModel):

    langchain_service = LangchainService()
    # chat_response = langchain_service.get_chat_response(request)

    chat_response = langchain_service.get_chat_response_with_history(request)

    if chat_response['context']:

        source_doc_list = langchain_service.get_source_doc_list(chat_response['context'])
        # print(source_doc_list)

        str_doc = ""
        for singdoc in source_doc_list:
            str_doc += "["+singdoc+"]"

        chat_answer = chat_response['answer']['answer'] 
        chat_answer = chat_answer + " " + str_doc

        follow_up_q_list = langchain_service.generate_queries(request.lastUserQuestion)

        str_follow_up_q = ""
        for sing_q in follow_up_q_list:
            sing_q = ''.join([i for i in sing_q if not i.isdigit()])
            sing_q = sing_q.replace("- ", "")
            str_follow_up_q += "<<"+sing_q+">>"

        chat_answer = chat_answer + " " + str_follow_up_q

        blob_storage = AzureBlobStorageService(blob_service_client=blob_service_client ,container_client=container_client)
        sas_url = blob_storage.get_sas_url_async(blob_name=source_doc_list[0])

        final_response = ApproachResponse(
            answer=chat_answer,
            thoughts=chat_response['answer']['thoughts'],
            data_points=langchain_service.get_data_points_response(chat_response['context']),
            # images=[
            #     SupportingImageRecord(title="Benefit_Options.pdf: Dummy Image 1", url="http://example.com/image1.jpg"),
            #     SupportingImageRecord(title="Benefit_Options.pdf: Dummy Image 2", url="http://example.com/image2.jpg"),
            # ],
            citation_base_url=sas_url
        )
    else:

        final_response = ApproachResponse(
            answer=chat_response['answer']['answer'],
            thoughts=chat_response['answer']['thoughts'],
            data_points=[
                SupportingContentRecord(title="", content="")
            ],
            citation_base_url="http://127.0.0.1:10000/devstoreaccount1/omnihub-container"
        )

    return ResponseModel(
        answer=final_response.answer,
        thoughts=final_response.thoughts,
        data_points=final_response.data_points,
        images=final_response.images,
        citation_base_url=final_response.citation_base_url,
        error=final_response.error
    )