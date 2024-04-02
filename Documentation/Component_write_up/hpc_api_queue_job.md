## Hpc_api endpoint queue_job

**Where:**  
Runs on the integration server.

**Inputs/conditions:**  
Receives a job_model:
- Asset_guid
- Job_name
- Job_id
- Timestamp

**Description:**  
Receives information that the job has been queued. Finds the assets in the track database and updates it with the received information.

**Outputs/Updates:**  
Updates asset in the track database:  
- `Jobs_list`
  - `Job_status`: QUEUED
  - `Job_id`
  - `Job_queued_time`

Returns an HTTP status code of 200 if everything updated correctly and 422 if things went wrong.

**Calls:**  
None
