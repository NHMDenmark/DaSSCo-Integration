## "metadata_updated_by"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
Metadata can be updated manually, via pipelines and via Specify 

**Value:**  
The name of the Pipeline that created the metadata. This will be picked from the "pipeline_name", sent under metadata creation.Fx PIEHERB0001

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Note  

**Updated where and when:**  
Never

**Maps to in ARS:**  
user in the event protocol

**Maps to in Specify:**  
None

**Issues:**  
We can only keep one value here despite the asset potentially having its metadata updated multiple times. 

