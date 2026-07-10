from typing import Dict, List
from pydantic import ConfigDict
from field_validation import SafeModel

class BarcodeModel(SafeModel):
    guid: str
    job: str
    status: str
    barcodes: List[str]
    asset_subject: str
    MSO: bool
    MOS: bool
    label: bool
    multi_specimen: bool = False
    disposable: str = None
    issues: List[Dict] = None

    model_config = ConfigDict(extra='forbid')