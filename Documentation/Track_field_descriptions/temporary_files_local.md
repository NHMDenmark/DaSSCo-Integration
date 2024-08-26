## "temporary_files_local"

**Type of field:**  
String  

**Part of which document:**  
Track data  

**Description:**  
A status telling us if the asset has files on the ingestion server.   

**Value:**  
YES

**Why do we have this field:**  
It lets us check if there are files that should be deleted once an asset is done being processed.

**Populated by whom and when:**  
Integration server when the asset files are being processed.  

**Updated where and when:**  
Does not get updated but it gets deleted at the end of the pipeline.