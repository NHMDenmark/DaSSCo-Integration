from typing import Dict, List, Optional
from pydantic import ConfigDict
from field_validation import SafeModel

class SearchModel(SafeModel):
    key_values: List[Dict]
    time_key: Optional[str] = None
    after: Optional[str] = None
    before: Optional[str] = None

    model_config = ConfigDict(extra='forbid')