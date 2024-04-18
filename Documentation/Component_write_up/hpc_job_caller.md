## Hpc_job_caller script

**Where:**  
Runs on the integration server.

**Inputs/conditions:**  
Requires that we can set up a SSH connection with an HPC server.  
Checks for assets in the track database where:
- `hpc_ready` status: YES
- `jobs_status`: WAITING

**Description:**  
This script runs continually, checking if its conditions are met.  
Sets up an SSH connection with the HPC server that it keeps open.  
Searches the track database for assets with the above conditions.  
If an asset is found, it finds the waiting jobs in the job list with the lowest priority rating and sends a command to the HPC server to run those job scripts with the asset. Updates the track database with job statuses.

**Outputs/Updates:**  
Updates asset in the track database:  
- `jobs_status`: STARTING  
- `jobs_list`:
  - `job_status`: STARTING  
Sends the following info in the call:  
- Path to the job script
- `asset_guid`

**Calls:**  
Job script on HPC server.

