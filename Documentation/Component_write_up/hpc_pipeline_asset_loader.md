## HPC_pipeline assetLoader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives three arguments on invocation:
- asset_guid
- HTTP link to image in file share
- batch_id

**Description:**  
This component loads image data files and metadata files of an asset into the local HPC memory. It loads the image data via the HTTP link to the image in the file share from ARS and the metadata from the integration server. It sends feedback to the integration server about:
a) whether it could queue the assetLoader into the execution queue and
b) when the asset has been loaded successfully.

**Outputs/Updates:**  
Sends the following info in the a) call to [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md):
- Asset_guid
- Job_name: assetLoader
- Job_id: HPC job ID if the queue is not already full, otherwise -1
- Timestamp

Sends the following info in the b) call to[HPC_pipeline_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md):
- Asset_guid

**Calls:**  
Calls [HPC_pipeline_feedbackQueue](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_feedbackQueue.md) and, in case of success, [HPC_pipeline_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md).
