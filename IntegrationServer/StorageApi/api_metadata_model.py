from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, Json
from Enums import asset_status_nt

class Tag(BaseModel):
    key: str
    value: str

class Specimen(BaseModel):
    institution: str = ""
    collection: str = ""
    barcode: str = ""
    specimen_pid: str = ""
    preparation_type: str = ""

class ApiMetadataModel(BaseModel):
    asset_pid: str = ""
    asset_guid: str = ""
    parent_guid: Optional[str] = None
    status: str = asset_status_nt.AssetStatusNT.WORKING_COPY.value # not optional must come from an enum list
    multi_specimen: bool = False
    specimens: List[Specimen] = []
    funding: str = ""
    subject: str = ""
    payload_type: str = "" # List[str] = []
    file_formats: List[str] = []
    asset_locked: bool = False
    restricted_access: List[str] = []
    audited: bool = False
    date_asset_taken: datetime = None
    institution: str = ""
    collection: str = ""
    pipeline: str = ""
    workstation: str = ""
    digitizer: str = ""
    tags: Dict[str, str] = {}
    
