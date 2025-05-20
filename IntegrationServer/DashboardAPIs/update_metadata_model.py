from typing import Dict, List, Optional
from pydantic import BaseModel

class UpdateMetadataModel(BaseModel):
    update_ars: bool = False
    key_values: Optional[Dict] = None
    asset_guids: List[str]