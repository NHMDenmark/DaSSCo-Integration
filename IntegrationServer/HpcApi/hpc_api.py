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
from metadata_model import MetadataAsset
from HpcApi import hpc_service
from HpcApi.update_model import UpdateAssetModel
from HpcApi.queue_model import QueueModel

"""
Rest api setup for receiving data from the slurm. 
"""

app = FastAPI()
util = utility.Utility()
service = hpc_service.SlurmService()
metadata_model = MetadataAsset
update_model = UpdateAssetModel
queue_model = QueueModel

@app.get("/")
def index():
    return "keep out"

# TODO receive metadata does not have unit test
@app.post("/api/v1/metadata_asset")
async def receive_metadata(metadata: metadata_model):
    service.persist_new_metadata(metadata)

@app.post("/api/v1/update_asset")
async def update_asset(update_data: update_model):
    updated = service.update_from_hpc(update_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/api/v1/queue_job")
async def queue_job(queue_data: queue_model):
    updated = service.job_queued(queue_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/api/v1/asset_ready")
async def asset_ready(asset_guid: str):
    updated = service.asset_ready(asset_guid)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.get("/api/v1/httplink")
def get_httplink(asset_guid: str):
    link = service.get_httplink(asset_guid)

    if link is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return link

@app.get("/api/v1/metadata_asset")
def get_metadata(asset_guid: str):
    asset = service.get_metadata_asset(asset_guid)

    if asset is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return asset   