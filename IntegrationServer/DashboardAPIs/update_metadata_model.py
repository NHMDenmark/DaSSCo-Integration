from typing import Dict, List, Optional
from field_validation import SafeModel
from pydantic import ConfigDict

class UpdateMetadataModel(SafeModel):
    update_ars: bool = False
    key_values: Optional[Dict] = None
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')