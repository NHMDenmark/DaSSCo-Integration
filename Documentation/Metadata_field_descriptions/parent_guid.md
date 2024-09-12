## "parent_guid"

**Type of field:**  
String  

**Part of which document:**  
Metadata

**Description:**  
This is the name of the parent media and in most cases will be the same as the original_parent_name, but can be different if a derivative of a derivative.

**Value:**  
None

**Why do we have this field:**  
Because it tells us something important  

**Populated by whom and when:**  
Running pipeline 

**Updated where and when:**  
Never

**Maps to in ARS:**  
parent_guid

**Maps to in Specify:**  
None

**Issues:**  
This field cannot have an empty string in ARS it must be "null" or an actual parent guid. There is a bug where it can be overwritten to null again (not sure exactly how this works though).

