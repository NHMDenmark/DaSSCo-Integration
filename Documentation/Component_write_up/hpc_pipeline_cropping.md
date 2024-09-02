## HPC_pipeline cropping

**Where:**  
Runs on the HPC cluster.

**Inputs/conditions:**  
Receives one argument on invocation:
- asset_guid

**Description:**  
This component crops the asset image.
The cropping algorithm works as follows:
1. An edge detection is run on the image, finding differences in channel intensities. The intensities are assumed to be important image features. The most extrem outliers create a rectangular bounding box for the edges.
2. The NHMD herbarium specific, L-shaped side ruler, is located in the image and its bounding box is calculated.
3. These two bounding boxes are combined to a new bounding box by using the maximum and minimum coordinates in the 4 directions (positive x, negative x, positive y, negative y), ensuring that the image is never cropped below the side ruler dimension, but in case more extreme outliers are found, the image is cropped to include those.


It saves the cropped image locally. It is save din the same batch folder under the name_guid__cropped.tif.

It reports to the [Hpc_api update_asset] endpoint that the job has finished.


**Outputs/Updates:**  


Sends the following info in the third call to [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md) endpoint:
- asset_guid
- Job_name: cropping
- Job_status: Done
- "data": { }

**Calls:**  
Calls [Hpc_api update_asset](https://github.com/NHMDenmark/DaSSCo-Integration/blob/main/Documentation/Component_write_up/hpc_api_update_asset.md).
