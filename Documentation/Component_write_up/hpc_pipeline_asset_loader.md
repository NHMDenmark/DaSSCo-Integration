## HPC_pipeline assetLoader

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives three arguments on invocation:
- asset_guid
- HTTP link to image in file share
- batch_id

**Description:**  
This component loads image data files and metadata files of an asset into the local HPC memory. It loads the image data via the HTTP link to the image in the file share from ARS and the metadata from the integration server. It sends feedback to the integration server about when the asset has been loaded successfully.

**Outputs/Updates:**  
Sends the following info in the call to[HPC_pipeline_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md):
- Asset_guid

**Calls:**  
Calls in case of success [HPC_pipeline_asset_ready](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_pipeline_asset_ready.md).
