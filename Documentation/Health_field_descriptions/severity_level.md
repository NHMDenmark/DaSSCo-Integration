## "severity_level"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Severity level indicator. Based on the logging library levels. We can add more levels if needed. Warnings are telling something isnt as it should be, but service is still going. Errors means something went wrong and we must look at it.  

**Value**
WARNING / ERROR

**Why do we have this field:**  
Lets us know how important/critical something is.  

**Populated by whom and when:**  
Sent to the health api by the service where the error occurred. Persisted in the health db.  

**Updated where and when:**  
Never
