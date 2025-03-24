from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, Json
from Enums import asset_status_nt

class Tag(BaseModel):
    key: str
    value: str

class IssueModel(BaseModel):
    category: str
    name: str
    timestamp: Optional[datetime] = None
    description: Optional[str] = None
    note: Optional[str] = None
    solved: bool = False

class LegalityModel(BaseModel):
    copyright: Optional[str] = None
    license: Optional[str] = None
    credit: Optional[str] = None

class Specimen(BaseModel):
    institution: str = ""
    collection: str = ""
    barcode: str = ""
    specimen_pid: str = ""
    preparation_type: str = ""

class ApiMetadataModel(BaseModel):
    asset_created_by: Optional[str] = None
    asset_deleted_by: Optional[str] = None
    asset_guid: str
    asset_pid: Optional[str] = None
    asset_subject: Optional[str] = None
    asset_updated_by: Optional[str] = None
    audited: bool = False
    audited_by: Optional[str] = None
    camera_setting_control: Optional[str] = None
    collection: str = ""
    complete_digitiser_list: List[str] = []
    date_asset_created_ars: Optional[datetime] = None
    date_asset_deleted_ars: Optional[datetime] = None
    date_asset_finalised: Optional[datetime] = None
    date_asset_taken: Optional[datetime] = None
    date_asset_updated_ars: Optional[datetime] = None
    date_audited: Optional[datetime] = None
    date_metadata_created_ars: Optional[datetime] = None
    date_metadata_ingested: Optional[datetime] = None
    date_metadata_updated_ars: Optional[datetime] = None
    date_pushed_to_specify: Optional[datetime] = None
    digitiser: Optional[str] = None
    external_publisher: List[str] = []
    file_formats: List[str] = []
    funding: List[str] = []
    institution: str = ""
    issue: List[IssueModel] = []
    legality: LegalityModel = LegalityModel()
    make_public: bool = False
    metadata_created_by: Optional[str] = None
    metadata_source: Optional[str] = None
    metadata_updated_by: Optional[str] = None
    metadata_version: Optional[str] = None
    mos_id: Optional[str] = None
    multi_specimen: bool = False
    parent_guid: List[str] = []
    payload_type: str = None
    pipeline: str = ""
    push_to_specify: bool = False
    restricted_access: List[str] = []
    status: str = asset_status_nt.AssetStatusNT.WORKING_COPY.value # not optional must come from an enum list
    tags: Dict[str, str] = {}
    workstation: str = ""
    asset_locked: bool = False # field not in integration servers metadata
    specimens: List[Specimen] = [] # contains preparation_type, barcode, specimen_pid