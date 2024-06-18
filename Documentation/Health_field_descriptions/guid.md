## "guid"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Optional field since not all entries have this. The guid for the asset the error occured with.   

**Value**
Asset guid

**Why do we have this field:**  
Lets us know which asset the error happened with.  

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db.  

**Updated where and when:**  
Never
