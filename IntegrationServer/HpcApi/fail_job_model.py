from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from field_validation import SafeModel

class FailJobModel(SafeModel):
    guid: str
    job_name: str
    job_id: str
    timestamp: datetime
    fail_status: str
    hpc_message: Optional[str] = "No message"
    hpc_exception: Optional[str] = None

    model_config = ConfigDict(extra='forbid')
