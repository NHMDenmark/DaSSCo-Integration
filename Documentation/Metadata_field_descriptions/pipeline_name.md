## "pipeline_name"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
The name of the Pipeline, which has sent an create, update or delete request to the storage service. It is the pipeline that creates the asset, but we will create derivatives (multiple assets per specimen), so will probably need to explore this in relation to specimen as well. Need to check if mandatory to create an asset (e.g., when adding assets other than via a mass digitisation pipeline).

**Value:**  
8 characters followed by 4 digitsFx PIPEHERB0001

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Running IngestionClient/pipeline

**Updated where and when:**  
Never

**Maps to in ARS:**  
pipeline

**Maps to in Specify:**  
None

**Issues:**  
Naming mapping issue

