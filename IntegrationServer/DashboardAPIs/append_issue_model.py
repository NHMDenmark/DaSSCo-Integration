from dassco_utils.metadata.models import IssueModel
from pydantic import BaseModel, ConfigDict
from typing import List

class AppendIssueModel(BaseModel):
    update_ars: bool
    issue: IssueModel
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')