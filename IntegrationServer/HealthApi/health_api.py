import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from HealthApi import health_service
from HealthApi.message_model import MessageModel
from HealthApi.run_status_change_model import RunStatusChangeModel
from HealthApi.pause_model import PauseModel

"""
Rest api for receiving warnings/errors and other log worthy incidents. 
Sends the message to the health service where further handling of the information happens. 
"""
# TODO api is only set up for local use. Would want more fletched out endpoint urls if we want it online.

health = FastAPI()
service = health_service.HealthService()
message_model = MessageModel
run_model = RunStatusChangeModel
pause_model = PauseModel

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

@health.post("/api/attempt_unpause")
async def attempted_unpause(info: pause_model):

    informed = service.attempted_unpause(info)

    return informed