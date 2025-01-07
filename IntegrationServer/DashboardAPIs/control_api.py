"""
Rest api for controlling various parts of the integration server. 
"""
import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from DashboardAPIs import control_service
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import utility

control = FastAPI()
util = utility.Utility()
service = control_service.ControlService()

@control.get("/control/check")
def index():
    return "check it out"

@control.post("/control/start_all")
async def start_all():

    running, already_running = service.all_run()

    if running is False:
        return JSONResponse(content={"error": "something went awry"}, status_code=500)
    
    if already_running is True:
        return JSONResponse(content={"status": "WAS RUNNING ALREADY"}, status_code=200)

    return JSONResponse(content={"status": "ALL RUNNING"}, status_code=200)

@control.post("/control/stop_all")
async def stop_all():

    stopped = service.stop_all()

    if stopped is False:
        return JSONResponse(content={"status": "ALL RUNNING"}, status_code=500)

    return JSONResponse(content={"status": "ALL STOPPING"}, status_code=200)

@control.post("/control/start_service")
async def service_start(service_name: str):

    started = service.start_service(service_name)
    
    if started is False:
        return JSONResponse(content={"status": f"Failed to start {service_name}"}, status_code=500)

    return JSONResponse(content={"status": f"Started {service_name}"}, status_code=200)