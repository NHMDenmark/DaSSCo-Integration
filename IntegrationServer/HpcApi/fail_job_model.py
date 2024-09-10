from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class FailJobModel(BaseModel):
    guid: str
    job_name: str
    job_id: str
    timestamp: datetime
    fail_status: str
    hpc_message: Optional[str] = "No message"
    hpc_exception: Optional[str] = None
