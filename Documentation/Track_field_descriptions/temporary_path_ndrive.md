## "temporary_path_ndrive"

**Type of field:**  
String  

**Part of which document:**  
Track data  

**Description:**  
Path to the ndrive directory where an assets files are. Being a temporary field this will get deleted once the asset has finished processing.  

**Value:**  
Path to a directory

**Why do we have this field:**  
It lets us know where to find an asset on the ndrive so it is easier to delete after the processing is done. It also allows us to easier restore an asset if somethign goes wrong.  

**Populated by whom and when:**  
Integration server when the asset files are being processed.  

**Updated where and when:**  
Does not get updated but it gets deleted at the end of the pipeline.