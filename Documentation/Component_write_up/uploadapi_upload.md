## UploadAPI upload script

**Where:**  
Runs on the refinery server under the url https://refinery.dassco.dk/upload.

**Inputs/conditions:**  
The input is a POST request with 
* username
* password
* content_type='image'
* assetName
* metadata file
* CSRF token
* checksum
* size
* image data


**Description:**  
This script receives the asset and some additional information. Then it cascades into multiple integrity checks
1. Saves the image and metadatafile on the N-Drive in a timestamped folder under the respective workstation folder.
2. Checks whether the size of the saved image is the same as the size information sent in the POST request.
3. Checks whether the checksum of the saved image is the same as the checksum information sent in the POST request.
4. Checks whether no asset of the same name already exists in the database.
2. If steps 2 to 4 have return Yes, the asset is put into the database and a positive status code is retured (200).
3. If any of the steps 2 to 4 have returned No, the asset is deleted and a negative status code is returned.


**Outputs/Updates:**  
One of hte following two options:
* 200 for successful upload
* everything else for no success in uploading 

**Calls:**  
N/A

