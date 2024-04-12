## "asset_created_by"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
An asset is created by a pipeline or sync with Specify. Hence this field will be the name of the pipeline that created the asset. It could also be created via a specific intervention - e.g., transferring assets from one place to another. Would it therefore be the person scripting this or logged on that appears as a name here?

**Values:**
The name of the Pipeline that deleted the asset. This will be picked from the "pipeline_name", sent under delete.
Fx PIPEHERB0001
**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Upon event

**Updated where and when:**  
Never
