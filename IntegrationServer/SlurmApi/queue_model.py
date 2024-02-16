from pydantic import BaseModel

class QueueModel(BaseModel):
    guid: str
    job_name: str
    job_id: str
    timestamp: str
    