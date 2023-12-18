from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List
import json
import os

"""
Rest api setup for receiving data from the slurm. 
"""
# TODO Separate this into its own repository. Too difficult to test with without having packaged everything else due to dependencies.
# Needs acces to the models.py and utility.py files. Currently they are just both copied into this file.
app = FastAPI()


class Check(BaseModel):
    id: str
    text: str
    optio: Optional[str]


class MetadataAsset(BaseModel):
    audited: Optional[str]
    audited_by: Optional[str]
    audited_date: Optional[str]
    institution: Optional[str]
    collection: Optional[str]
    barcode: Optional[str]
    specimen_pid: Optional[str]
    date_asset_created: Optional[str]
    date_asset_deleted: Optional[str]
    date_asset_updated: Optional[List[str]]
    date_metadata_created: Optional[str]
    date_metadata_updated: Optional[List[str]]
    asset_created_by: Optional[str]
    asset_deleted_by: Optional[str]
    asset_updated_by: Optional[List[str]]
    metadata_created_by: Optional[str]
    metadata_updated_by: Optional[List[str]]
    digitiser: Optional[str]
    restricted_access: Optional[str]
    external_publisher: Optional[List[str]]
    file_format: Optional[List[str]]
    payload_type: Optional[str]
    asset_subject: Optional[str]
    funding: Optional[str]
    asset_guid: Optional[str]
    asset_pid: Optional[str]
    multispecimen: Optional[str]
    other_multispecimen: Optional[List[str]]
    tags: Optional[List[str]]
    asset_taken_date: Optional[str]
    original_parent: Optional[str]
    parent: Optional[str]
    pipeline_name: Optional[str]
    preparation_type: Optional[str]
    workstation_name: Optional[str]
    original_specify_media_name: Optional[str]
    specify_attachment_id: Optional[str]
    pushed_to_specify_date: Optional[str]
    related_media: Optional[List[str]]
    status: Optional[str]
    asset_locked: Optional[str]
    storage_location: Optional[str]
    taxon_name: Optional[str]
    type_status: Optional[str]
    geographic_region: Optional[str]
    ocr_text: Optional[str]
    specimen_storage_location: Optional[str]
    CREATED_BY: Optional[str]
    media_guid: Optional[str]


"""
Class with helper methods that are used throughout the different processes.
Mostly contains functions that has to do with reading/updating .json files. 
"""


class Utility:
    def __init__(self):
        pass

    def read_json(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data

    def get_value(self, file_path, key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data.get(key)

    def get_nested_value(self, file_path, key, nested_key):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)

            # Use get method to access the nested keys
            if key in data and nested_key in data[key]:
                return data[key][nested_key]
            else:
                return None

    def write_full_json(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def update_json(self, file_path, key, value):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data[key] = value
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    # Example: Utility.update_layered_json(Utility, "./ssh_connections_config.json", ["connection1", "port"], "23")
    def update_layered_json(self, file_path, keys, value):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        current_level = data

        # Navigate through the nested keys to reach the last level
        for key in keys[:-1]:
            current_level = current_level[key]

        # Update the value at the last level
        current_level[keys[-1]] = value

        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def find_keys_with_value(self, dictionary, target_value):
        result_keys = []

        for key, value in dictionary.items():
            if value == target_value:
                result_keys.append(key)

        return result_keys

    def error_occurred(self, asset_path):
        pass  # TODO
        """ 
        look for READY or INPIPELINE in _jobs change to ERROR
        Create folder structure /FilesError/"pipeline_name"/ move guid folder here
        """


util = Utility()


@app.get("/")
def index():
    return "keep out"


@app.post("/api/v1/check")
async def receive_check(check: Check):
    check_json = check.__dict__
    util.write_full_json(f"../Files/UpdatedFiles/{check.id}.json", check_json)


@app.post("/api/v1/metadata_asset")
async def receive_metadata(metadata: MetadataAsset):
    metadata_json = metadata.__dict__
    util.write_full_json(f"../Files/UpdatedFiles/{metadata.asset_guid}.json", metadata_json)


@app.post("/api/v1/jobs")
async def receive_jobs(check: Check):
    pass  # TODO make job model, decide on status list, connect with mongo db.
