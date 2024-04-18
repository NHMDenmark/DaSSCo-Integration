## HPC_pipeline assetDeleter

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component deletes an asset (image data and metadata files) from the local HPC memory. It sends feedback to the integration server about whether it could queue the assetDeleter into the execution queue.

**Outputs/Updates:**  
Sends the following info in the call to Hpc_api endpoint queue_job:
- Asset_guid
- Job_name: assetDeleter
- Job_id: HPC job ID if the queue is not already full, otherwise -1
- Timestamp

**Calls:**  
Calls Hpc_api endpoint queue_job.
