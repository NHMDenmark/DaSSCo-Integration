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
from DashboardAPIs.update_track_model import UpdateTrackhModel
from DashboardAPIs.update_metadata_model import UpdateMetadataModel
from DashboardAPIs.append_issue_model import AppendIssueModel
from DashboardAPIs.update_issue_model import UpdateIssueModel

control = FastAPI()
util = utility.Utility()
service = control_service.ControlService()
search_model = SearchModel
update_track_model = UpdateTrackhModel
update_metadata_model = UpdateMetadataModel
append_issue_model = AppendIssueModel
update_issue_model = UpdateIssueModel

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
async def get_track_data(key: str, value: str):

    found, msg = service.get_health_asset_data(key, value)

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

@control.post("/control/search_in_metadata")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_metadata_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any assets with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list

@control.post("/control/search_in_track")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_track_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any assets with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list

@control.post("/control/search_in_health")
async def search_in_metadata(search_model: search_model):

    found, data_list, msg = service.search_health_db(search_model)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    if data_list == []:
        return JSONResponse(content={"message": "failed to find any entries with these criteria"}, status_code=200)
    
    if data_list is None:
        return JSONResponse(content={"message": msg}, status_code=422)

    return data_list

@control.put("/control/update_track_data")
async def update_track_data(update_track_model: update_track_model):
    
    updated, msg = service.update_track_data(update_track_model)

    if updated is False:
        return JSONResponse(content={"update_status": updated, "message": msg}, status_code=500)
    
    return JSONResponse(content={"update_status": updated, "message": msg}, status_code=200)

@control.get("/control/get_service_data")
async def run_status(service_name: str):

    found, msg = service.get_service_data(service_name)

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.get("/control/get_all_service_data")
async def get_all_service_data():

    found, msg = service.get_all_service_data()

    if found is False:
        return JSONResponse(content={"status": msg}, status_code=500)
    
    return msg

@control.put("/control/update_metadata")
async def update_metadata(update_metadata_model: update_metadata_model):
    
    updated, msg = service.update_metadata(update_metadata_model)

    if updated is False:
        return JSONResponse(content={"update_status": updated, "message": msg}, status_code=500)
    
    return JSONResponse(content={"update_status": updated, "message": msg}, status_code=200)

@control.put("/control/append_issue")
async def append_issue(append_issue_model: append_issue_model):
    
    updated, msg = service.append_issue_to_metadata(append_issue_model)

    if updated is False:
        return JSONResponse(content={"update_status": updated, "message": msg}, status_code=500)
    
    return JSONResponse(content={"update_status": updated, "message": msg}, status_code=200)

@control.put("/control/update_issue")
async def update_issue(update_issue_model: update_issue_model):

    updated, msg = service.update_issue(update_issue_model)

    if updated is False:
        return JSONResponse(content={"update_status": updated, "message": msg}, status_code=500)
    
    return JSONResponse(content={"update_status": updated, "message": msg}, status_code=200)