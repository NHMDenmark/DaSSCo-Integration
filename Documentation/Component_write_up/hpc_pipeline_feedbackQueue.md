## HPC_pipeline feedbackQueue

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives three arguments on invocation:
- asset_guid
- job ID
- job name

**Description:**  
This component reports whether the queue has space to put in the _job name_ module. If so, it returns the job ID as the SLURM job ID. If not, it returns the job ID as -1.

**Outputs/Updates:**  
Sends the following info in the call to [Hpc_api endpoint queue_job](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_queue_job.md):
- Asset_guid
- Job_name: job name
- Job_id: HPC job ID if the queue is not already full, otherwise -1
- Timestamp

**Calls:**  
Calls [Hpc_api endpoint queue_job](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_queue_job.md).
