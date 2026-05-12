import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI, Depends, Request   
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from HealthApi.message_model import MessageModel
from HealthApi.run_status_change_model import RunStatusChangeModel
from HealthApi.pause_model import PauseModel
from HealthApi.unexpected_error_model import UnexpectedErrorModel
"""
Rest api for receiving warnings/errors and other log worthy incidents. 
Sends the message to the health service where further handling of the information happens.
This is not exposed to the internet and is only for internal use by the integration server and its components. 
"""
# "health" is the name - to run api in terminal be in folder and: nohup uvicorn health_api:health --reload --host 127.0.0.1 --port 8555 &

message_model = MessageModel
run_model = RunStatusChangeModel
pause_model = PauseModel
unexpected_error_model = UnexpectedErrorModel

@asynccontextmanager
async def lifespan(health: FastAPI):
    

    from MongoDB.mongo_connection import MongoSharedClient
    from HealthApi import health_service

    health.state.mongo_client = MongoSharedClient()
    health.state.service = health_service.HealthService(health.state.mongo_client)

    yield

    health.state.mongo_client.close()

health = FastAPI(lifespan=lifespan)

def get_service(request: Request):
    return request.app.state.service

@health.get("/")
def index():
    return "sickening!!"

@health.post("/api/warning")
async def receive_warning(warning: message_model, service = Depends(get_service)):
    
    handled = service.receive_warning(warning)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle warning."}, status_code=422)

    #print(handled)
    return handled

@health.post("/api/error")
async def receive_error(error: message_model, service = Depends(get_service)):
    
    handled = service.receive_error(error)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle error"}, status_code=422)

    #print(handled)
    return handled

@health.post("/api/run_change_status")
async def run_status_change(info: run_model, service = Depends(get_service)):

    print(info)

    informed = service.run_status_change(info)
    
    if informed is False:
        return JSONResponse(content={"error": "failed to inform of status change"}, status_code=422)

    return informed

@health.post("/api/attempt_unpause")
async def attempted_unpause(info: pause_model, service = Depends(get_service)):

    informed = service.attempted_unpause(info)

    if informed is False:
        return JSONResponse(content={"error": "failed to inform of attempted unpause"}, status_code=422)

    return informed

@health.post("/api/unexpected_error")
async def unexpected_error(info: unexpected_error_model, service = Depends(get_service)):

    handled = service.unexpected_error(info)

    if handled is False:
        return JSONResponse(content={"error": "failed to handle unexpected error"}, status_code=422)

    return handled

@health.post("/api/create_health_entry")
async def create_health_entry(info: message_model, service = Depends(get_service)):

    created = service.create_health_entry(info)

    if created is False:
        return JSONResponse(content={"error": "failed to create entry for health db."}, status_code=422)
    
    return created