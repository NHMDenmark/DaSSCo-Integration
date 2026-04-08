from pydantic import BaseModel
from typing import List

class UpdateARSMetadataListModel(BaseModel):
    asset_guids: List[str]