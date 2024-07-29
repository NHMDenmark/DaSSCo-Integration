from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    guid: Optional[str] = None
    service_name: str
    flag: Optional[str] = None
    flag_status: Optional[str] = None
    message: str