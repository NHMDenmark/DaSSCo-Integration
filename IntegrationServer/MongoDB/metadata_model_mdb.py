from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

"""
Model class for the metadata file according to github documentation.
"""

class MetadataAsset(BaseModel):
    asset_created_by: Optional[str]
    asset_deleted_by: Optional[str]
    asset_guid: Optional[str]
    asset_locked: Optional[bool]
    asset_pid: Optional[str]
    asset_subject: Optional[str]
    date_asset_taken: Optional[datetime]
    asset_updated_by: Optional[str]
    date_metadata_uploaded: Optional[datetime]
    date_asset_finalised: Optional[datetime]
    audited: Optional[bool]
    audited_by: Optional[str]
    audited_date: Optional[datetime]
    barcode: Optional[List[str]]
    collection: Optional[str]
    date_asset_created: Optional[datetime]
    date_asset_deleted: Optional[datetime]
    date_asset_updated: Optional[List[datetime]]
    date_metadata_created: Optional[datetime]
    date_metadata_updated: Optional[List[datetime]]
    digitiser: Optional[str]
    external_publisher: Optional[List[str]]
    file_format: Optional[List[str]] # Should be an Enum of file formats
    funding: Optional[str]
    institution: Optional[str]
    metadata_created_by: Optional[str]
    metadata_updated_by: Optional[str]
    metadata_uploaded_by: Optional[str]
    multispecimen: Optional[bool]
    parent_guid: Optional[str]
    payload_type: Optional[str] # Optional[List[str]]
    pipeline_name: Optional[str]
    preparation_type: Optional[str] # Optional[List[str]]
    pushed_to_specify_date: Optional[datetime]
    restricted_access: Optional[bool] # or a Optional[List[str]] from the restricted access enum
    specimen_pid: Optional[str] # keys being barcodes and the values are currently unknown Optional[List[dict]]
    status: Optional[str]
    tags: Optional[Dict[str, str]] # basically a way to add comments
    workstation_name: Optional[str]