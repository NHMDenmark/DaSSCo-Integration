from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

"""
Model class for metadata v3.0.3, used for referencing.
"""
class IssueModel(BaseModel):
    category: str
    name: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    solved: bool = False

class LegalityModel(BaseModel):
    copyright: Optional[str] = None
    license: Optional[str] = None
    credit: Optional[str] = None

class ExternalPublisherModel(BaseModel):
    name: str

class MetadataModel(BaseModel):
    asset_created_by: Optional[str] = None
    asset_deleted_by: Optional[str] = None
    asset_guid: str
    asset_pid: Optional[str] = None
    asset_subject: Optional[str] = None
    asset_updated_by: Optional[str] = None
    audited: bool = False
    audited_by: Optional[str] = None
    barcode: List[str] = []
    camera_setting_control: Optional[str] = None
    collection: str
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
    external_publishers: List[ExternalPublisherModel] = []
    file_format: Optional[str] = None
    funding: List[str] = []
    institution: str
    issues: List[IssueModel] = []
    legality: LegalityModel = LegalityModel()
    make_public: bool = False
    metadata_created_by: Optional[str] = None
    metadata_source: Optional[str] = None
    metadata_updated_by: Optional[str] = None
    metadata_version: Optional[str] = "v3.0.3"
    mime_type: Optional[str] = None
    mos_id: Optional[str] = None
    multi_specimen: bool = False
    parent_guids: List[str] = []
    payload_type: Optional[str] = None
    pipeline_name: str
    preparation_type: List[str] = []
    push_to_specify: bool = False
    restricted_access: List[str] = []
    session_id: Optional[str] = None # this only exist in integration and ingestion client. ARS does not have this field.
    specify_attachment_remarks: Optional[str] = None
    specify_attachment_title: Optional[str] = None
    specimen_pid: Optional[str] = None
    status: Optional[str] = None
    tags: Dict[str, str] = {}
    workstation_name: str
