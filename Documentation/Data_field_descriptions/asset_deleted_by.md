## "asset_deleted_by"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
An asset could be deleted by a pipeline (and therefore the name of the pipeline that deleted the asset will be shown here. This is taken from pipeline_name). An asset could also be deleted by a member of the project team if they have sufficient privileges. Mostly this will be very rare after the asset has been locked. A record of the file should remain even if the asset no longer exists if deleted following locking of the asset (post processing).

**Value**
The name of the Pipeline that deleted the asset. This will be picked from the "pipeline_name", sent under delete.
Fx PIPEHERB0001

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Upon event

**Updated where and when:**  
Never
