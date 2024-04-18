## HPC_pipeline job started

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives three arguments on invocation:
- asset_guid
- job_name
- job_ID

**Description:**  
This component reports when a job has started execution in the queue.

**Outputs/Updates:**  
Sends the following info in the call to [HPC_api_start_job](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_start_job.md):
- Asset_guid
- Job_name: 
- Job_id: HPC job ID if the queue is not already full, otherwise -1
- Timestamp

Sends the following info in the b) call to Hpc_api endpoint asset_ready:
- Asset_guid

**Calls:**  
Calls[HPC_api_start_job](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_start_job.md).
