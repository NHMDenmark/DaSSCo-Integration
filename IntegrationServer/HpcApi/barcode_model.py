from typing import Dict, List
from pydantic import BaseModel, Field

class BarcodeModel(BaseModel):
    guid: str
    job: str
    status: str
    barcodes: List[str]
    asset_subject: str
    MOS: bool
    label: bool
    disposable: str = None