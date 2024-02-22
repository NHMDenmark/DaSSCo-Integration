import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List, Dict
import utility
from metadata_model import MetadataAsset
from SlurmApi import slurm_service
from SlurmApi.update_model import UpdateAssetModel
from SlurmApi.queue_model import QueueModel

"""
Rest api setup for receiving data from the slurm. 
"""

app = FastAPI()
util = utility.Utility()
service = slurm_service.SlurmService()
metadata_model = MetadataAsset
update_model = UpdateAssetModel
queue_model = QueueModel

@app.get("/")
def index():
    return "keep out"

@app.post("/api/v1/metadata_asset")
async def receive_metadata(metadata: metadata_model):
    service.persist_new_metadata(metadata)

# TODO send success message back to slurm?
@app.post("/api/v1/update_asset")
async def update_asset(update_data: update_model):
    service.update_from_slurm(update_data)

@app.post("/api/v1/queue_job")
async def queue_job(queue_data: queue_model):
    service.job_queued(queue_data)
     