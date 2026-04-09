from typing import List
from pydantic import ConfigDict
from field_validation import SafeModel

class UpdateARSMetadataListModel(SafeModel):
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')