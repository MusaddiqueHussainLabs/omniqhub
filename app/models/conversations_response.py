from typing import List, Optional
from pydantic import BaseModel, AnyHttpUrl

# class SupportingContentRecord:
#     def __init__(self, title: str, content: str):
#         self.title = title
#         self.content = content

# class SupportingImageRecord:
#     def __init__(self, title: str, url: str):
#         self.title = title
#         self.url = url

# class ApproachResponse:
#     def __init__(self, answer: str, citation_base_url: str, thoughts: Optional[str] = None, data_points: Optional[List[SupportingContentRecord]] = None, images: Optional[List[SupportingImageRecord]] = None, error: Optional[str] = None):
#         self.answer = answer
#         self.thoughts = thoughts
#         self.data_points = data_points or []
#         self.images = images or []
#         self.citation_base_url = citation_base_url
#         self.error = error

class SupportingContentRecord(BaseModel):
    title: str
    content: str

class SupportingImageRecord(BaseModel):
    title: str
    url: AnyHttpUrl

class ApproachResponse(BaseModel):
    answer: str
    citation_base_url: AnyHttpUrl
    thoughts: Optional[str] = None
    data_points: Optional[List[SupportingContentRecord]] = None
    images: Optional[List[SupportingImageRecord]] = None
    error: Optional[str] = None