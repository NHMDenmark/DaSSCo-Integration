import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List, Dict
import utility
from HpcApi.metadata_model import MetadataAsset
from HpcApi import hpc_service
from HpcApi.update_model import UpdateAssetModel
from HpcApi.job_model import JobModel
from HpcApi.barcode_model import BarcodeModel

"""
Rest api setup for receiving data from hpc. 
"""

app = FastAPI()
# app.mount("/display", StaticFiles(directory="/work/data/lars/displayer/page"), name='/display')

util = utility.Utility()
service = hpc_service.HPCService()
metadata_model = MetadataAsset
update_model = UpdateAssetModel
barcode_model = BarcodeModel
job_model = JobModel

@app.get("/")
def index():
    return "keep out both of you"

@app.get("/api/test")
def test():
    return "test complete"


"""
Deprecated since we use the derivative endpoint instead.
# TODO receive metadata does not have unit test
@app.post("/api/v1/metadata_asset")
async def receive_metadata(metadata: metadata_model):
    service.persist_new_metadata(metadata)
"""
    
# TODO receive derivative does not have unit test
@app.post("/api/v1/derivative")
async def receive_derivative_metadata(metadata: metadata_model):
    
    received = service.received_derivative(metadata)

    if received is False:
        return JSONResponse(content={"error": "derivative fail"}, status_code=422)


@app.post("/api/v1/update_asset")
async def update_asset(update_data: update_model):
    updated = service.update_from_hpc(update_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/api/v1/barcode")
async def insert_barcode(barcode_data: barcode_model):

    updated = service.insert_barcode(barcode_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)


@app.post("/api/v1/queue_job")
async def queue_job(queue_data: job_model):
    updated = service.job_queued(queue_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post("/api/v1/start_job")
async def start_job(start_data: job_model):
    started = service.job_started(start_data)

    if started is False:
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

    return {"link": link}

# TODO want to receive more info here, we need to update asset size and add files to list of files in track db that info is something HPC has
@app.post("/api/v1/derivative_uploaded")
async def derivative_files_uploaded(asset_guid: str):

    uploaded = service.derivative_files_uploaded(asset_guid)

    if uploaded is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.get("/api/v1/metadata_asset")
def get_metadata(asset_guid: str):
    asset = service.get_metadata_asset(asset_guid)

    if asset is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return asset   
"""
@app.get("/api/display/{folder_name}")
def get_file_names(folder_name: str):
    paths = service.get_file_paths(folder_name)

    return paths

@app.get("/api/v1/nifi/{input}")
def get_nifi_check(input: str):
    if input == "true":
        return JSONResponse(content={"input": "input was true"}, status_code=200)
    else:
        return JSONResponse(content={"input": "input was not true"}, status_code=200)
"""
