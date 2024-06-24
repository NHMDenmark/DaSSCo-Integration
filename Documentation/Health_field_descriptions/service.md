## "service"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
The name of the micro service that encountered the warning/error. 

**Value:**  
fex: Asset creator HPC

**Why do we have this field:**  
Lets us know which service encountered the bug.   

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db. 

**Updated where and when:**  
Never
