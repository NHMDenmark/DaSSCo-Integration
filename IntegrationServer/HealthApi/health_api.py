import sys
import os
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

from fastapi import FastAPI
from HealthApi import health_service
from HealthApi.message_model import MessageModel

health = FastAPI()
service = health_service.HealthService()
message_model = MessageModel

@health.get("/")
def index():
    return "sickeningly"

@health.post("/api/warning")
async def receive_warning(warning: message_model):
    
    handled = service.receive_warning(warning)
    
    return handled