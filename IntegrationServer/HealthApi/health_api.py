import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from HealthApi import health_service

health = FastAPI()
service = health_service.HealthService()

@health.get("/")
def index():
    return "sickening"

@health.post("/api/warning")
def receive_warning(warning: str, guid: str = None):
    
    service.receive_warning(warning, guid)

    
    return True