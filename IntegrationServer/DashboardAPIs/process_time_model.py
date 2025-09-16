from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ProcessTimeModel(BaseModel):
    
    metadata_origin: List[str] = []
    before_date: Optional[str] = None
    after_date: Optional[str] = None
    min_seconds: Optional[int] = None
    max_seconds: Optional[int] = None
    asset_guids: List[str] = []

    model_config = ConfigDict(extra='forbid')