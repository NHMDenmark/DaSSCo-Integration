from typing import Optional
from pydantic import ConfigDict
from field_validation import SafeModel

class MessageModel(SafeModel):
    guid: Optional[str] = None
    service_name: str
    flag: Optional[str] = None
    flag_status: Optional[str] = None
    message: str

    model_config = ConfigDict(extra='forbid')