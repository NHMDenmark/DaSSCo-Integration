#!/bin/sh

#PBS -W group_list=ku_00273 -A ku_00273

#PBS -N apicheck
### Only send mail when job is aborted or terminates abnormally
#PBS -m n
### Number of nodes
#PBS -l nodes=1:thinnode:ppn=1
### Memory
#PBS -l mem=10mb
### Requesting time - format is <days>:<hours>:<minutes>:<seconds>
#PBS -l walltime=00:01:00

workdir=/home/projects/ku_00273/people/lardam/job_test/
cd $workdir

# Load all required modules for the job
module load tools
module load anaconda3/4.4.0

# activate the conda environment
source activate cenv

# call script that calls api
python get_bool_from_api.py

# wait for python script to finish
wait

# write the updated bool in output file
echo $APIBOOL

conda deactivate