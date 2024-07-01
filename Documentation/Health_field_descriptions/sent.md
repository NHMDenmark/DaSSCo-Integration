## "sent"

**Type of field:**  
String  

**Part of which document:**  
Health

**Description:**  
Denoting if a mail was sent with the information in this entry.  

**Value:**  
YES or NO

**Why do we have this field:**  
Lets us check when the last time a mail was sent out. This allows us to not spam the inbox too much with repeating errors.  

**Populated by whom and when:**  
Created by the health api service when an entry is added to the health db. Initial value is NO.  

**Updated where and when:**  
When a mail is sent, the value changes to YES. 
