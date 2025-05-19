from typing import Dict, List, Optional
from pydantic import BaseModel
from dassco_utils.metadata.models import IssueModel

class UpdateMetadataModel(BaseModel):
    update_ars: bool = False
    key_values: Optional[Dict] = None
    append_issue: Optional[IssueModel] = None
    asset_guids: List[str]