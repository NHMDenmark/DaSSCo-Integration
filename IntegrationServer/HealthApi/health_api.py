import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from HealthApi import health_service
from HealthApi.message_model import MessageModel
from HealthApi.run_status_change_model import RunStatusChangeModel

health = FastAPI()
service = health_service.HealthService()
message_model = MessageModel
run_model = RunStatusChangeModel

@health.get("/")
def index():
    return "sickeningly"

@health.post("/api/warning")
async def receive_warning(warning: message_model):
    
    handled = service.receive_warning(warning)
    #print(handled)
    return handled

@health.post("/api/error")
async def receive_error(error: message_model):
    
    handled = service.receive_error(error)
    #print(handled)
    return handled

@health.post("/api/run_change_status")
async def run_status_change(info: run_model):

    informed = service.run_status_change(info)
    
    return informed