## "message"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Written message in the code that gets transferred to the health service through the health api. 

**Value**
Any type of message that will help understanding what is happening.

**Why do we have this field:**  
Allows us add content to a warning or error beyond the exception.

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db. 

**Updated where and when:**  
Never
