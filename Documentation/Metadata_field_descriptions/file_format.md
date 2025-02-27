## "file_format"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
The format of the asset

**Value:**  
tif, jpeg, raf

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Running IngestionClient/pipeline 

**Updated where and when:**  
Never

**Maps to in ARS:**  
file_formats

**Maps to in Specify:**  
File Format

**Issues:**  
Name mapping issue. We are using a single value in lower case. ARS is using a list of values all in upper case that must come from a enum list. Specify is using a single value I think. What happens if assets can have thumbnails (jpegs) added to them?

