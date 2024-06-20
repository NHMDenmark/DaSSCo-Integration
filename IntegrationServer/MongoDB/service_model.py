from pydantic import BaseModel, Field
from typing import Optional, List

"""
Model class for the micro service table.
"""

class ServiceModel(BaseModel):
    _id: Optional[str]
    run_status: str = "RUNNING"

class ModelService:

    def __init__(self):

        self._ide = ""
        self.run_status = "RUNNING"

    def create_model(self, name):
        
        entry = {"_id": name,
                 "run_status": self.run_status
                 }
        return entry


