import azure.functions as func
import logging
import os
import getpass

from langchain_community.document_loaders import AzureBlobStorageContainerLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.redis import Redis

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import PyPDFLoader

from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)

from dotenv import load_dotenv
load_dotenv(override=True)

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass("Provide your Google API key here")

vector_store_address: str = os.environ["AZURE_SEARCH_ENDPOINT"]
vector_store_password: str = os.environ["AZURE_SEARCH_ADMIN_KEY"]

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embedding_function = embeddings.embed_query

fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=len(embedding_function("Text")),
        vector_search_profile_name="myHnswProfile",
    ),
    SearchableField(
        name="metadata",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    # Additional field to store the title
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    # Additional field for filtering on document source
    SimpleField(
        name="source",
        type=SearchFieldDataType.String,
        filterable=True,
    ),
]

index_name: str = os.environ["AZURE_SEARCH_ENDPOINT_INDEX_NAME"]
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embedding_function,
    fields=fields,
)

# from app.services.langchain_service import LangchainService

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="embed-blob")
@app.blob_trigger(arg_name="myblob", path=os.environ['AZURE_STORAGE_BLOB_CONTAINERS'],
                               connection="AzureWebJobsStorage") 
def BlobTrigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    file_name = os.path.basename(myblob.name)
    loader = AzureBlobStorageContainerLoader(conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"], 
                                         container=os.environ['AZURE_STORAGE_BLOB_CONTAINERS'],
                                         prefix=file_name)

    documents = loader.load_and_split()
    vector_store.add_documents(documents=documents)
    

