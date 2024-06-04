from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    guid: Optional[str] = None
    service: str
    flag: Optional[str] = None
    message: str