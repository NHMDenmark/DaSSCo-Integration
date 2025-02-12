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
from DashboardAPIs.search_model import SearchModel

control = FastAPI()
util = utility.Utility()
service = control_service.ControlService()
search_model = SearchModel

@control.get("/control/check")
def index():
    return "check it out!"

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

@control.post("/control/stop_service")
async def service_stop(service_name: str):

    stopped = service.stop_service(service_name)

    if stopped is False:
        return JSONResponse(content={"status": f"Failed to stop {service_name}"}, status_code=500)

    return JSONResponse(content={"status": f"Stopping {service_name}"}, status_code=200)

@control.get("/control/get_track_data")
async def get_track_data(guid: str):

    found, msg = service.get_track_asset_data(guid)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_metadata")
async def get_track_data(guid: str):

    found, msg = service.get_metadata_asset_data(guid)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_health_data")
async def get_track_data(guid: str):

    found, msg = service.get_health_asset_data(guid)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_throttle_data")
async def get_track_data():

    found, msg = service.get_throttle_data()

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_error_lists")
async def get_error_lists():

    found, msg = service.get_list_of_guids_with_error_flag()

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_critical_error_lists")
async def get_critical_error_lists():

    found, msg = service.get_list_of_guids_with_critical_error_flag()

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/search_in_metadata")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_metadata_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any assets with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list

@control.get("/control/search_in_track")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_track_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any assets with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list

@control.get("/control/search_in_health")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_health_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any entries with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list