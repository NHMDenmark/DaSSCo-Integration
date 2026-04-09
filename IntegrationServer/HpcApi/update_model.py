from typing import Dict
from pydantic import ConfigDict
from field_validation import SafeModel

class UpdateAssetModel(SafeModel):
    guid: str
    job: str
    status: str
    data: Dict

    model_config = ConfigDict(extra='forbid')