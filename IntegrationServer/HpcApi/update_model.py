from typing import Dict
from pydantic import BaseModel

class UpdateAssetModel(BaseModel):
    guid: str
    job: str
    status: str
    data: Dict