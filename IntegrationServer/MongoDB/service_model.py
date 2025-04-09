from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

"""
Model class for the micro service table.
"""

class ServiceModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    run_status: str = "STOPPED"
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None

class ModelService:

    def __init__(self):

        self.service_model = ServiceModel()
        
    def create_model(self, name):
        
        self.service_model = ServiceModel()

        self.service_model.id = name

        self.service_model = self.service_model.model_dump(by_alias=True)

        return self.service_model