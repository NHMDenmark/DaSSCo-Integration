from pydantic import BaseModel

class PauseModel(BaseModel):
    service_name: str
    run_status: str
    pause_counter: int
    message: str