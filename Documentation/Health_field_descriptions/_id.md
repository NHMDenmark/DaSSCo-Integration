## "_id"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Unique identifier for the entry. Made from the prefix_id from the service the entry originates from, and the modified timestamp of when the entry was logged.     

**Value:**  
String. Example: AcA_20240619141354373

**Why do we have this field:**  
Needed as the database unique identifier.  

**Populated by whom and when:**  
Integration servers health api when entry is created for the health db. 

**Updated where and when:**  
Never
