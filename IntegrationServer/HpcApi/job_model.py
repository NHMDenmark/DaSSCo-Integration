from pydantic import ConfigDict
from datetime import datetime
from field_validation import SafeModel

class JobModel(SafeModel):
    guid: str
    job_name: str
    job_id: str
    timestamp: datetime

    model_config = ConfigDict(extra='forbid')
    