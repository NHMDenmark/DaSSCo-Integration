import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List, Dict
import utility
from MongoDB import mongo_connection
from MongoAPI import metadata_model_mdb_api as mmma
from MongoAPI import link_model, mongo_service

"""
Api for querying the mongo db instead of directly accessing it. Useful if parts of the integration server needs to be deployed separately. 
Usage of this api in the other parts of the overall service will need to be implemented/refactored.
"""

mongo_app = FastAPI()
util = utility.Utility()

metadata = mmma.MetadataModel
filelinks = link_model.FileLinksModel

ms = mongo_service.MongoService()

@mongo_app.get("/")
def index():
    return "keep mongo free"

@mongo_app.post("/api/v1/create_asset_entries")
async def create_asset_entries(metadata: metadata, file_links: filelinks):
    http_status, msg = ms.create_new_asset_entries(metadata, file_links)
    return JSONResponse(content={f"status": {msg}}, status_code=http_status)

@mongo_app.get("/api/v1/get_metadata/{guid}")
def get_metadata(guid: str):
    http_status, metadata = ms.get_metadata(guid)
    return JSONResponse(content=metadata, status_code=http_status)

# TODO ensure we send barcodes and other strings that want to be lists of in actual lists
@mongo_app.put("/api/v1/update_metadata/{guid}")
def update_metadata(guid: str, data: Dict):
    http_status, metadata = ms.update_metadata(guid, data)
    return JSONResponse(content=metadata, status_code=http_status)

@mongo_app.get("/api/v1/get_entry/{mdbname}/{key}/{value}")
def get_entry(mdbname: str, key: str, value: str):

    http_status, entry = ms.get_entry(mdbname, key, value)

    return JSONResponse(content=entry, status_code=http_status)

@mongo_app.put("/api/v1/update_entry/{mdbname}/{guid}/{key}/{value}")
def update_entry(mdbname: str, guid: str, key: str, value: str):

    http_status, entry = ms.update_entry_key_value(mdbname, guid, key, value)

    return JSONResponse(content=entry, status_code=http_status)


