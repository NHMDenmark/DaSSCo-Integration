from typing import Dict, List
from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    guid: str = None
    service: str
    flag: str = None
    message: str