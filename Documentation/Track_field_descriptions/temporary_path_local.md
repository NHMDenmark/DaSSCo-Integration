## "temporary_path_local"

**Type of field:**  
String  

**Part of which document:**  
Track data  

**Description:**  
Path to the local directory for an asset. Being a temporary field this will get deleted once the asset has finished processing.  

**Value:**  
Path to a directory

**Why do we have this field:**  
It lets us know where to find an asset on the integration server while the asset is being processed.  

**Populated by whom and when:**  
Integration server when the asset files are being processed.  

**Updated where and when:**  
Does not get updated but it gets deleted at the end of the pipeline.  