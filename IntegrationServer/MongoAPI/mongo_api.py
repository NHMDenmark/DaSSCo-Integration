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
from MongoDB import mongo_connection

"""
Api for querying the mongo db instead of directly accessing it. Useful if parts of the integration server needs to be deployed separately. 
Usage of this api in the other parts of the overall service will need to be implemented/refactored.
"""

mongo_app = FastAPI()
util = utility.Utility()
mongo_track = mongo_connection.MongoConnection("track")
mongo_metadata = mongo_connection.MongoConnection("metadata")
mongo_batch = mongo_connection.MongoConnection("batch")
mongo_slurm_list = mongo_connection.MongoConnection("slurm")
mongo_slurm_availability = mongo_connection.MongoConnection("availability")


@mongo_app.get("/")
def index():
    return "keep mongo free"

@mongo_app.post("/api/v1/create_track_entry")
async def create_track_entry(guid: str, pipeline: str):
      mongo_track.create_track_entry(guid, pipeline)

@mongo_app.post("/api/v1/create_metadata_entry")
async def create_metadata_entry(json_path: str, guid: str):
    mongo_metadata.create_metadata_entry(json_path, guid)

"""

@mongo_app.put("/api/v1/update_entry"):
async def update_entry(guid: str, key: str, value: str):


    def update_entry(self, guid, key, value):
    

        query = {"_id": guid}
        update_data = {"$set": {key: value}}

        self.collection.update_one(query, update_data)
"""