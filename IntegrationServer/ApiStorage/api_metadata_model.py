from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Tag(BaseModel):
    key: str
    value: str

class Specimen(BaseModel):
    institution: str
    collection: str
    barcode: str
    specimen_pid: str
    preparation_type: List[str]

class ApiMetadataModel(BaseModel):
    asset_pid: str
    asset_guid: str
    parent_guid: Optional[str] = None
    status: str # not optional must come from an enum list
    multi_specimen: bool
    specimens: List[Specimen] = []
    funding: str
    subject: str
    payload_type: str
    file_formats: List[str]
    asset_locked: bool
    restricted_access: List[str] = []
    audited: bool
    date_asset_taken: datetime
    institution: str
    collection: str
    pipeline: str
    workstation: str
    digitizer: str
    tags: List[Tag] = []