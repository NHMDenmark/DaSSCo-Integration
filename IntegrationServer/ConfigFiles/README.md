## job_detail_config.json

## pipeline_job_config.json

## slurm_config.json
Sets the maximum amount of jobs we want to have queued up at the same time.
```bash
    "max_queued_jobs": 10
```
Sets the maximum number of jobs the slurm server will process at the same time. 
```bash
    "parallel_jobs": 3
```
Sets the maximum total expected amount of time in hours we want to have queued up at the same time.
```bash
    "total_expected_time": 30
```

## ssh_connections_config.json
