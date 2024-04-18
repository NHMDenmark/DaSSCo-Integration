## "jobs_status"

**Type of field:**  
String, from the status enum  

**Part of which document:**  
Track

**Description:**  
Uses the status enum to show the overall status for the job flow. Most active job defines the status. 

**Why do we have this field:**  
This lets us keep track of the overall progression of the jobs/processes an asset needs to go through with on the hpc server.  

**Populated by whom and when:**  
Integration server. When the asset is received.  

**Updated where and when:**  
Integration server. Whenever a job changes its status this will check if the overall status also needs to change.
