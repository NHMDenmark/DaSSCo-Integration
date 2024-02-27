from pydantic import BaseModel
from datetime import datetime

class QueueModel(BaseModel):
    guid: str
    job_name: str
    job_id: str
    timestamp: datetime
    