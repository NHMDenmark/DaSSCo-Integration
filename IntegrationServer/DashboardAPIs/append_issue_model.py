from dassco_utils.metadata.models import IssueModel
from pydantic import ConfigDict
from typing import List
from field_validation import SafeModel

class AppendIssueModel(SafeModel):
    update_ars: bool
    issue: IssueModel
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')