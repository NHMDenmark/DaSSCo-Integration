## "exception"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Optional field since not all entries have this. The exception that caused the warning/error. This is a fully written out exception.  

**Value:**  
Stacktrace - for technical eyes.

**Why do we have this field:**  
It helps us find and fix the bug that occurred. Gives us precise information about the bug.

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db.

**Updated where and when:**  
Never
