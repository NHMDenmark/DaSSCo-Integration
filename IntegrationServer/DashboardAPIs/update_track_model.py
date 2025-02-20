from typing import Dict, List, Optional
from pydantic import BaseModel

class UpdateTrackhModel(BaseModel):
    key_values: Optional[Dict] = None
    job_name: Optional[str] = None
    job_key_values: Optional[Dict] = None
    asset_guids: List[str]