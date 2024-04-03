## "status"

**Type of field:**  
String from the status enum 

**Part of which document:**  
Track

**Description:**  
Part of the job object populating the job_list. Uses the status enum to show status of an individual job.  

**Why do we have this field:**  
It lets us keep track of each jobs status.   

**Populated by whom and when:**  
Integration server. When the jobs list is populated.   

**Updated where and when:**  
Integration server. When a job is queued, started, finished or some kind of error occurs. This will be communicated to the integration server via the hpc api from the hpc server. 
