from pydantic import ConfigDict
from typing import List, Dict
from field_validation import SafeModel

class UpdateIssueModel(SafeModel):
    
    issue_category: str
    issue_name: str
    key_values: Dict[str, str]
    update_ars: bool
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')