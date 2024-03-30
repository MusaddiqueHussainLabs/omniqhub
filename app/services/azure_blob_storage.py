import os
from typing import List, Union
import typing
# from pdfsharp.pdf import PdfDocument, PdfDocumentOpenMode
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    BlobSasPermissions,
    ContainerSasPermissions,
    UserDelegationKey,
    generate_container_sas,
    generate_blob_sas,
    ContentSettings
)
# from azure.identity import DefaultAzureCredential
from aiohttp import web
import asyncio
from enum import Enum
from typing import AsyncIterable, Dict
from urllib.parse import urljoin
from dataclasses import dataclass
import datetime

from fastapi import UploadFile

from dotenv import load_dotenv
load_dotenv(override=True)

class DocumentProcessingStatus(Enum):
    NotProcessed = 0
    Succeeded = 1
    Failed = 2

class DocumentResponse:
    def __init__(self, name, content_type, content_length, last_modified, uri, document_processing_status, embedding_type):
        self.name = name
        self.content_type = content_type
        self.content_length = content_length
        self.last_modified = last_modified
        self.uri = uri
        self.document_processing_status = document_processing_status
        self.embedding_type = embedding_type

class AzureBlobStorageService:
    def __init__(self, blob_service_client: BlobServiceClient, container_client: ContainerClient):
        self.blob_service_client = blob_service_client
        self.container_client = container_client
        # self.default_credential = DefaultAzureCredential()

    async def upload_files_async(self, files: list[UploadFile]):
        try:
            uploaded_files = []
            for file in files:
                file_name = file.filename
                if file_name.lower().endswith('.pdf'):

                    # Create a blob client using the local file name as the name for the blob
                    blob_client = self.blob_service_client.get_blob_client(container=os.environ["AZURE_STORAGE_BLOB_CONTAINERS"], blob=file_name)

                    file_content = await self.read_file_content(file)
                    content_settings = ContentSettings(content_type="application/pdf")
                    
                    blob_client.upload_blob(file_content, blob_type="BlockBlob")
                    blob_client.set_http_headers(content_settings=content_settings)

                    uploaded_files.append(file_name)

            if not uploaded_files:
                return {"uploaded_files": uploaded_files, "is_successful": False, "error": "No files were uploaded. Either the files already exist or the files are not PDFs or images."}
            
            return {"uploaded_files": uploaded_files, "is_successful": True, "error": ""}
        except Exception as ex:
            raise ex

    @staticmethod
    def blob_name_from_file_page(filename: str, page: int = 0) -> str:
        if filename.lower().endswith('.pdf'):
            return f"{os.path.splitext(filename)[0]}-{page}.pdf"
        return os.path.basename(filename)

    @staticmethod
    async def read_file_content(file) -> bytes:
        file_content = await file.read()
        return file_content
    
    async def on_get_documents_async(self) -> AsyncIterable[DocumentResponse]:
        response_list = []
        response_struc: typing.Dict[str, typing.Any] = {}

        blob_list = self.container_client.list_blobs(include=["metadata"])

        for blob in blob_list:
            
            # Get a BlobClient for a specific blob
            blob_client = self.container_client.get_blob_client(blob.name)

            # Create a SAS token that's valid for one day, as an example
            start_time = datetime.datetime.now(datetime.timezone.utc)
            expiry_time = start_time + datetime.timedelta(minutes=30)

            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=blob_client.container_name,
                blob_name=blob_client.blob_name,
                account_key=os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
                permission=BlobSasPermissions(read=True),
                expiry=expiry_time,
                start=start_time
            )
            sas_url = f"{blob_client.url}?{sas_token}"
            
            properties = blob_client.get_blob_properties()
            response_struc['name'] = str(blob.name)
            response_struc['content_type'] = str(properties.content_settings.content_type)
            response_struc['size'] = int(properties.size)
            response_struc['last_modified'] = properties.last_modified.astimezone(None)
            response_struc['status'] = DocumentProcessingStatus.Succeeded
            response_struc['url'] = sas_url

            response_list.append(response_struc.copy())
            
        return response_list
    
    def get_sas_url_async(self, blob_name) -> str:
        # Get a BlobClient for a specific blob
        blob_client = self.container_client.get_blob_client(blob_name)

        # Create a SAS token that's valid for one day, as an example
        start_time = datetime.datetime.now(datetime.timezone.utc)
        expiry_time = start_time + datetime.timedelta(minutes=30)

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time,
            start=start_time
        )
        sas_url = f"{blob_client.url}?{sas_token}"

        return sas_url
            