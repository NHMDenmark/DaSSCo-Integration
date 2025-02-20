from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SearchModel(BaseModel):
    key_values: List[Dict]
    time_key: Optional[str] = None
    after: Optional[str] = None
    before: Optional[str] = None
