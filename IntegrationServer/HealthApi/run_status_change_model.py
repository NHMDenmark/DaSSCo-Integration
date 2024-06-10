from pydantic import BaseModel

class RunStatusChangeModel(BaseModel):
    service_name: str
    run_status: str
    message: str