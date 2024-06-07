## HPC_pipeline cropping&derivatives

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component crops the asset image, downsamples it to 400 ppi (TIF) and 72 ppi (JPEG) and saves them locally on the HPC. It copies the parent's metadata and populates the metadata file field "parent_guid" with the received asset_guid.
The cropping algorithm works as follows:
1. An edge detection is run on the image, finding differences in channel intensities. The intensities are assumed to be important image features. The most extrem outliers create a rectangular bounding box for the edges.
2. The NHMD herbarium specific, L-shaped side ruler, is located in the image and its bounding box is calculated.
3. These two bounding boxes are combined to a new bounding box by using the maximum and minimum coordinates in the 4 directions (positive x, negative x, positive y, negative y), ensuring that the image is never cropped below the side ruler dimension, but in case more extreme outliers are found, the image is cropped to include those.


It creates two new guids by increasing the derivative specific numerals.
Example: 
asset_guid received         7e8-3-0f-0a-1a-0c-0-001-00-000-08e212-00000
asset_guid 400 ppi (TIF)    7e8-3-0f-0a-1a-0c-0-001-00-001-08e212-00000
asset_guid 72 ppi (JPEG)    7e8-3-0f-0a-1a-0c-0-001-00-002-08e212-00000

It then sends two requests to create new assets with the respective guids,images & metadata.
It reports to the [Hpc_api update_asset] endpoint that the job has finished.

**Outputs/Updates:**  
Sends the following info in the first call to [Hpc_api create new asset]() endpoint:
- asset_guid 400 ppi (TIF)
- metadata file

Sends the following info in the second call to [Hpc_api create new asset]() endpoint:
- asset_guid 72 ppi (JPEG)
- metadata file

Sends the following info in the third call to [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md) endpoint:
- asset_guid
- Job_name: cropping&derivative
- Job_status: Done
- "data": { }

**Calls:**  
Calls [Hpc_api create new asset]  twice, followed by [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md).
