from typing import List
from pydantic import ConfigDict
from field_validation import SafeModel

class GUIDListModel(SafeModel):
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')