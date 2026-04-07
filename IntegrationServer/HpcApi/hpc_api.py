"""
Rest api for receiving data and providing information to and from hpc. 
"""
import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI, Depends, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import utility
from dassco_utils.metadata import MetadataModel
from HpcApi.update_model import UpdateAssetModel
from HpcApi.job_model import JobModel
from HpcApi.barcode_model import BarcodeModel
from HpcApi.file_info_model import FileInfoModel
from HpcApi.fail_job_model import FailJobModel
from HpcApi.fail_derivative_creation_model import FailDerivativeCreationModel
from KeycloakInterface.auth import verify_token

util = utility.Utility()
metadata_model = MetadataModel
update_model = UpdateAssetModel
barcode_model = BarcodeModel
job_model = JobModel
fail_job_model = FailJobModel
file_info_model = FileInfoModel
fail_derivative_creation_model = FailDerivativeCreationModel

load_dotenv()   
front_url = os.getenv("HPC_FRONT_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    from MongoDB.mongo_connection import MongoSharedClient
    from HpcApi import hpc_service

    app.state.mongo_client = MongoSharedClient()
    app.state.service = hpc_service.HPCService(app.state.mongo_client)

    yield

    app.state.mongo_client.close()

app = FastAPI(lifespan=lifespan)

def get_service(request: Request):
    return request.app.state.service

@app.get(f"{front_url}/yo")
def index(user: dict = Depends(verify_token)):
    return {"message":"keep out all devils!!", "user": user["preferred_username"]}

@app.get(f"{front_url}/pub")
def index():
    return {"message":"keep out all devils!"}
    
@app.post(f"{front_url}/api/v1/derivative")
async def receive_derivative_metadata(metadata: metadata_model, service = Depends(get_service)):
    
    received = service.receive_derivative_metadata(metadata)

    if received is False:
        return JSONResponse(content={"error": "derivative fail."}, status_code=422)


@app.post(f"{front_url}/api/v1/update_asset")
async def update_asset(update_data: update_model, service = Depends(get_service)):
    updated = service.update_from_hpc(update_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)

@app.post(f"{front_url}/api/v1/barcode")
async def insert_barcode(barcode_data: barcode_model, service = Depends(get_service)):

    updated = service.insert_barcode(barcode_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)

@app.post(f"{front_url}/api/v1/queue_job")
async def queue_job(queue_data: job_model, service = Depends(get_service)):
    updated = service.job_queued(queue_data)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.post(f"{front_url}/api/v1/start_job")
async def start_job(start_data: job_model, service = Depends(get_service)):
    started = service.job_started(start_data)

    if started is False:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)

@app.post(f"{front_url}/api/v1/failed_job")
async def failed_job(fail_data: fail_job_model, service = Depends(get_service)):
    failed = service.job_failed(fail_data)

    if failed is False:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)

@app.post(f"{front_url}/api/v1/asset_ready")
async def asset_ready(asset_guid: str, service = Depends(get_service)):
    updated = service.asset_ready(asset_guid)

    if updated is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

@app.get(f"{front_url}/api/v1/httplink")
def get_httplink(asset_guid: str, service = Depends(get_service)):
    link = service.get_httplink(asset_guid)

    if link is None:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)

    return {"link": link}

@app.get(f"{front_url}/api/v1/metadata_asset")
def get_metadata(asset_guid: str, service = Depends(get_service)):
    asset = service.get_metadata_asset(asset_guid)

    if asset is None:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)

    return asset

# formerly known as derivative_file_uploaded - slurm calls
@app.post(f"{front_url}/api/v1/derivative_uploaded")
async def file_uploaded(asset_guid: str, service = Depends(get_service)):
    uploaded = service.derivative_files_uploaded(asset_guid)

    if uploaded is False:
        return JSONResponse(content={"error": "asset not found for file uploaded"}, status_code=422)
    
@app.post(f"{front_url}/api/v1/derivative_file_info")
async def file_info(file_info: file_info_model, service = Depends(get_service)):
    added = service.add_derivative_file(file_info)

    if added is False:
        return JSONResponse(content={"error": "asset not found for file info"}, status_code=422)

# confirmation endpoint for asset having been cleaned up on hpc
@app.post(f"{front_url}/api/v1/asset_clean_up")
async def asset_clean_up(asset_guid: str, service = Depends(get_service)):
    cleaned = service.clean_up(asset_guid)

    if cleaned is False:
        return JSONResponse(content={"error": "asset not found"}, status_code=422)
    
# derivative creation fail endpoint, not the same as the job failed - sometimes derivatives dont get created for various reasons
@app.post(f"{front_url}/api/v1/fail_derivative_creation")
async def fail_derivative_creation(info: fail_derivative_creation_model, service = Depends(get_service)):
    acknowledged = service.fail_derivative_creation(info)

    if acknowledged is False:
        return JSONResponse(content={"error": "asset not found."}, status_code=422)
