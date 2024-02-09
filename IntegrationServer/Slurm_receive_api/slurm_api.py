import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)


from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List, Dict
import json
import utility
import metadata_model
from Slurm_receive_api import slurm_service

"""
Rest api setup for receiving data from the slurm. 
"""

app = FastAPI()
util = utility.Utility()
metadata_asset = metadata_model.BaseModel()
service = slurm_service.SlurmService()

@app.get("/")
def index():
    return "keep out"

"""
class Check(BaseModel):
    id: str
    text: str
    optio: Optional[str]

@app.post("/api/v1/check")
async def receive_check(check: Check):
    check_json = check.__dict__
    util.write_full_json(f"../Files/UpdatedFiles/{check.id}.json", check_json)
"""

@app.post("/api/v1/metadata_asset")
async def receive_metadata(metadata: metadata_asset):
    metadata_json = metadata.__dict__
    util.write_full_json(f"IntegrationServer/Files/NewFiles/Derivatives/{metadata.asset_guid}.json", metadata_json)

@app.post("/api/v1/update_asset")
async def update_asset(guid: str, job: str, status: str, data: Dict):
    service.update_from_slurm(guid, job, status, data)


@app.post("/api/v1/jobs")
async def receive_jobs(check: None):
    pass  # TODO make job model, decide on status list, connect with mongo db.
