## "flag"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Optional field since not all entries have this. This will let us know which flag if any was updated due to the error. Assets with changed flags should enter an alternate flow.

**Value**
Value from the flag_enum list. "is_in_ars"

**Why do we have this field:**  
Lets us know if the asset had its flag changed due to the error.   

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db. 

**Updated where and when:**  
Never
