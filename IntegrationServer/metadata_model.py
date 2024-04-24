from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

"""
Model class for the metadata file as it is when its received from the digitisation process. 
"""
# TODO replaced datetime with str due to the way our jsons currently look. Have to decide if we will use None instead of "" when we dont have a timestamp yet.
class MetadataAsset(BaseModel):
    asset_created_by: Optional[str]
    asset_deleted_by: Optional[str]
    asset_guid: Optional[str]
    asset_locked: Optional[bool]
    asset_pid: Optional[str]
    asset_subject: Optional[str]
    date_asset_taken: Optional[str]
    asset_updated_by: Optional[str]
    metadata_uploaded_by: Optional[str]
    date_metadata_uploaded: Optional[str]
    date_asset_finalised: Optional[str]
    audited: Optional[bool]
    audited_by: Optional[str]
    audited_date: Optional[str]
    barcode: Optional[List[str]]
    collection: Optional[str]
    date_asset_created: Optional[str]
    date_asset_deleted: Optional[str]
    date_asset_updated: Optional[str]
    date_metadata_created: Optional[str]
    date_metadata_updated: Optional[str]
    digitiser: Optional[str]
    external_publisher: Optional[List[str]]
    file_format: Optional[str]
    funding: Optional[str]
    institution: Optional[str]
    metadata_created_by: Optional[str]
    metadata_updated_by: Optional[str]
    multispecimen: Optional[bool]
    parent_guid: Optional[str]
    payload_type: Optional[str]
    pipeline_name: Optional[str]
    preparation_type: Optional[str]
    pushed_to_specify_date: Optional[str]
    restricted_access: Optional[bool]
    specimen_pid: Optional[str]
    status: Optional[str]
    tags: Optional[Dict[str, str]]
    workstation_name: Optional[str]
