from typing import Dict, List, Optional
from field_validation import SafeModel
from pydantic import ConfigDict

class UpdateTrackModel(SafeModel):
    key_values: Optional[Dict[str, str]] = None
    job_name: Optional[str] = None
    job_key_values: Optional[Dict[str, str]] = None
    barcode_specimen_dict: Optional[Dict[str, int]] = None
    asset_guids: List[str]

    model_config = ConfigDict(extra='forbid')