from pydantic import ConfigDict
from typing import List, Optional
from field_validation import SafeModel

class ProcessTimeModel(SafeModel):
    
    metadata_origin: List[str] = []
    before_date: Optional[str] = None
    after_date: Optional[str] = None
    min_seconds: Optional[int] = None
    max_seconds: Optional[int] = None
    asset_guids: List[str] = []

    model_config = ConfigDict(extra='forbid')