## "priority"

**Type of field:**  
Integer  

**Part of which document:**  
Track

**Description:**  
Part of the job object populating the job_list. Used for knowing in which order job scripts are called. Job order is set in the pipeline_job_config file. Jobs with the same priority will be run in parallel on the hpc server. The lowest priority number will run before first.  

**Why do we have this field:**  
It allows us to control in which order pipeline jobs are run.   

**Populated by whom and when:**  
Integration server. When the job list is populated.   

**Updated where and when:**  
Never
