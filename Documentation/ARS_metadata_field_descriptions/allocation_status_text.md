## "allocation_status_text"

**Type of field:**  
String  

**Part of which document:**  
ARS

**Description:**  
A detailed error message if an error happens

**Value:**  
SUCCESS  : A share was successfully created or allocation was successfully changed. DISK_FULL : There is not enough disk space for the requested allocation. BAD_REQUEST : Changing the storage allocation to a lower amount than than is already used. UPSTREAM_ERROR : An issue with an external system happened. It could be a failure to download the parent asset from ERDA or a call to asset service from the file-proxy that fails. SHARE_NOT_FOUND : The share you are trying to update doesnt exist. INTERNAL_ERROR : Some unexpected internal error happened.

**Why do we have this field:**  
Gives us information about the status of the call made to ARS.

**Populated by whom and when:**  
ARS. Populated as part of the httpInfo protocol

**Updated where and when:**  
When the assets fileshare changes

