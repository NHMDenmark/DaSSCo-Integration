#!/bin/bash
sbatch <<EOT
#!/bin/bash


#SBATCH --job-name=test_job
#SBATCH --array 1-"$1"%"$2"
#SBATCH --cpus-per-task=1
#SBATCH --time=00:01:00

python /work/dassco_23_request/ldam/job_test.py \$SLURM_ARRAY_TASK_ID
python /work/dassco_23_request/ldam/second_job.py \$SLURM_ARRAY_TASK_ID

EOT