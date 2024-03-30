from typing import Union, Optional, List

from uuid import UUID
from pydantic import BaseModel, Field, validator, AnyHttpUrl

from app.models.conversations_response import SupportingContentRecord, SupportingImageRecord

from langchain_core import pydantic_v1
from langchain_core.output_parsers import BaseOutputParser

class Conversations(BaseModel):
    conversationId: Union[str, None] = None
    access_token: Union[str, None] = None
    expires_in: Union[int, None] = None
    streamUrl: Union[str, None] = None

# class RequestItem(BaseModel):
#     user: str
#     bot: Optional[str]

# class RequestOverrides(BaseModel):
#     semanticRanker: Optional[bool]
#     retrievalMode: int
#     semanticCaptions: Optional[str]
#     excludeCategory: Optional[str]
#     top: int
#     temperature: Optional[str]
#     promptTemplate: Optional[str]
#     promptTemplatePrefix: Optional[str]
#     promptTemplateSuffix: Optional[str]
#     suggestFollowupQuestions: bool

# class RequestModel(BaseModel):
#     history: List[RequestItem]
#     overrides: RequestOverrides
#     lastUserQuestion: str
#     approach: int

# class ResponseModel(BaseModel):
#     answer: str
#     thoughts: Optional[str] = None
#     data_points: Optional[List[SupportingContentRecord]] = None
#     images: Optional[List[SupportingImageRecord]] = None
#     citation_base_url: str
#     error: Optional[str] = None
    
class RequestItem(BaseModel):
    user: str
    bot: Optional[str]

class RequestOverrides(BaseModel):
    semanticRanker: Optional[bool]
    retrievalMode: int
    semanticCaptions: Optional[str]
    excludeCategory: Optional[str]
    top: int
    temperature: Optional[str]
    promptTemplate: Optional[str]
    promptTemplatePrefix: Optional[str]
    promptTemplateSuffix: Optional[str]
    suggestFollowupQuestions: bool

class RequestModel(BaseModel):
    history: List[RequestItem]
    overrides: RequestOverrides
    lastUserQuestion: str
    approach: int

class ResponseModel(BaseModel):
    answer: str
    thoughts: Optional[str] = None
    data_points: Optional[List[SupportingContentRecord]] = None
    images: Optional[List[SupportingImageRecord]] = None
    citation_base_url: AnyHttpUrl
    error: Optional[str] = None    

class ChatResponseModel(pydantic_v1.BaseModel):
    answer: str = pydantic_v1.Field(description="the answer to the question, If no source available, put the answer as I don't know.")
    thoughts: str = pydantic_v1.Field(description="""brief thoughts on how you came up with the answer, e.g. what sources you used, what you thought about, etc.""")

class LineListOutputParser(BaseOutputParser[List[str]]):
    """Output parser for a list of lines."""

    def parse(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        return lines