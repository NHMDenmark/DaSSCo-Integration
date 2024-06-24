## "metadata_created_by"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
Metadata could be created via a DaSSCo refinery pipeline, a scripted event (still a pipeline?) or via Specify

**Value:**  
The name of the Pipeline that created the metadata. This will be picked from the "pipeline_name", sent under metadata creation.
Fx PIPEHERB0001 

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Running IngestionClient/pipeline

**Updated where and when:**  
Never
