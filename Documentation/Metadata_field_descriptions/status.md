## "status"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
The status of the asset. It is not for the services use but for human eyes to quickly give an overview.  

**Value:**  
For processing, being processed, working copy, archive, processing halted, for deletion, issue with media, issue with metadata

**Why do we have this field:**  
Because it tells us something important - nope, currently we are not using this for anything. 

**Populated by whom and when:**  
Populated by integration server just before upload if empty.   

**Updated where and when:**  
Never

**Maps to in ARS:**  
status

**Maps to in Specify:**  
None

**Issues:**  
We don�t use this. It must be populated for an asset to get created in ARS. Missing decisions.

