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
from HpcApi.job_model import JobModel
from HpcApi.barcode_model import BarcodeModel
from HpcApi.file_info_model import FileInfoModel
from HpcApi.fail_job_model import FailJobModel

"""
Rest api setup for receiving data from hpc. 
"""

app = FastAPI()
util = utility.Utility()
service = hpc_service.HPCService()
metadata_model = MetadataAsset
update_model = UpdateAssetModel
barcode_model = BarcodeModel
job_model = JobModel
fail_job_model = FailJobModel
file_info_model = FileInfoModel


@app.get("/dev/yo")
def index():
    return "keep out all"

"""
Deprecated since we use the derivative endpoint instead.
# TODO receive metadata does not have unit test
@app.post("/dev/api/v1/metadata_asset")
async def receive_metadata(metadata: metadata_model):
    service.persist_new_metadata(metadata)
"""
    
# TODO receive derivative does not have unit test
@app.post("/dev/api/v1/derivative")
async def receive_derivative_metadata(metadata: metadata_model):
    received = service.receive_derivative_metadata(metadata)

    if received is False:
        return JSONResponse(content={"error": "derivative fail"}, status_code=422)


@app.post("/dev/api/v1/update_asset")
async def update_asset(update_data: update_model):
    updated = service.update_from_hpc(update_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/dev/api/v1/barcode")
async def insert_barcode(barcode_data: barcode_model):

    updated = service.insert_barcode(barcode_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)


@app.post("/dev/api/v1/queue_job")
async def queue_job(queue_data: job_model):
    updated = service.job_queued(queue_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/dev/api/v1/start_job")
async def start_job(start_data: job_model):
    started = service.job_started(start_data)

    if started is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/dev/api/v1/failed_job")
async def failed_job(fail_data: fail_job_model):
    failed = service.job_failed(fail_data)

    if failed is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/dev/api/v1/asset_ready")
async def asset_ready(asset_guid: str):
    updated = service.asset_ready(asset_guid)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.get("/dev/api/v1/httplink")
def get_httplink(asset_guid: str):
    link = service.get_httplink(asset_guid)

    if link is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return {"link": link}

@app.get("/dev/api/v1/metadata_asset")
def get_metadata(asset_guid: str):
    asset = service.get_metadata_asset(asset_guid)

    if asset is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return asset

@app.post("/dev/api/v1/derivative_file_uploaded")
async def file_uploaded(asset_guid: str):
    uploaded = service.derivative_files_uploaded(asset_guid)

    if uploaded is False:
        return JSONResponse(content={"error": "asset not found for file uploaded"}, status_code=422)
    
@app.post("/dev/api/v1/derivative_file_info")
async def file_info(file_info: file_info_model):
    added = service.add_derivative_file(file_info)

    if added is False:
        return JSONResponse(content={"error": "asset not found for file info"}, status_code=422)

# confirmation endpoint for asset having been cleaned up on hpc
@app.post("/dev/api/v1/asset_clean_up")
async def file_uploaded(asset_guid: str):
    cleaned = service.clean_up(asset_guid)

    if cleaned is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)