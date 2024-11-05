import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from HealthApi import health_service
from HealthApi.message_model import MessageModel
from HealthApi.run_status_change_model import RunStatusChangeModel
from HealthApi.pause_model import PauseModel
from HealthApi.unexpected_error_model import UnexpectedErrorModel
"""
Rest api for receiving warnings/errors and other log worthy incidents. 
Sends the message to the health service where further handling of the information happens. 
"""
# TODO api is only set up for local use. Would want more fletched out endpoint urls if we want it online.

# healt is the name - to run api in terminal be in folder and: nohup uvicorn health_api:health --reload --host 127.0.0.1 --port 8555 &
health = FastAPI()
service = health_service.HealthService()
message_model = MessageModel
run_model = RunStatusChangeModel
pause_model = PauseModel
unexpected_error_model = UnexpectedErrorModel

@health.get("/")
def index():
    return "sickeningly"

@health.post("/api/warning")
async def receive_warning(warning: message_model):
    
    handled = service.receive_warning(warning)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle warning"}, status_code=422)

    #print(handled)
    return handled

@health.post("/api/error")
async def receive_error(error: message_model):
    
    handled = service.receive_error(error)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle error."}, status_code=422)

    #print(handled)
    return handled

@health.post("/api/run_change_status")
async def run_status_change(info: run_model):

    informed = service.run_status_change(info)
    
    if informed is False:
        return JSONResponse(content={"error": "failed to inform of status change"}, status_code=422)

    return informed

@health.post("/api/attempt_unpause")
async def attempted_unpause(info: pause_model):

    informed = service.attempted_unpause(info)

    if informed is False:
        return JSONResponse(content={"error": "failed to inform of attempted unpause"}, status_code=422)

    return informed

@health.post("/api/unexpected_error")
async def unexpected_error(info: unexpected_error_model):

    handled = service.unexpected_error(info)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle unexpected error"}, status_code=422)

    return handled

@health.post("/api/create_health_entry")
async def create_health_entry(info: message_model):

    created = service.create_health_entry(info)

    if created is False:
        return JSONResponse(content={"error": "failed to create entry for health db."}, status_code=422)
    
    return created