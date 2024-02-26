from typing import Union, Optional

from uuid import UUID
from pydantic import BaseModel, Field, validator

class Conversations(BaseModel):
    conversationId: Union[str, None] = None
    access_token: Union[str, None] = None
    expires_in: Union[int, None] = None
    streamUrl: Union[str, None] = None