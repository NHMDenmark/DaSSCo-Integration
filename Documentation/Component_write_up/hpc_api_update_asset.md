## Hpc_api endpoint update_asset

**Where:**  
Runs on the integration server.

**Inputs/conditions:**  
Receives an update model:
- asset_guid
- job_name
- job_status
- Dictionary of field: values

**Description:**  
Receives an update model when the endpoint is called. Updates the track database with the new job status. If the status of the received info is DONE, updates the metadata database with the received dictionary info. This could be anything we discover during any pipeline/job on the HPC. Updates the track database to reflect that the asset has new metadata that needs to go to ARS.

**Outputs/Updates:**  
Update in metadata database:  
- Received fields in the dictionary

Update in track database:  
- job_status
- update_metadata
- jobs_list
  - job_status: received status

Returns an HTTP status code of 200 if everything updated correctly and 422 if things went wrong.

**Calls:**  
None.
