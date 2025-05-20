from pydantic import BaseModel, ConfigDict
from typing import List, Dict

class UpdateIssueModel(BaseModel):
    
    issue_category: str
    issue_name: str
    key_values: Dict[str, str]
    update_ars: bool
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')