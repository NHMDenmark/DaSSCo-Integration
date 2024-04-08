
#!/bin/sh
### Note: No commands may be executed until after the #PBS lines

#PBS -W group_list=ku_00273 -A ku_00273

#PBS -N job_2
### Output files (comment out the next 2 lines to get the job name used instead)
#PBS -e test.err
#PBS -o test.log
### Only send mail when job is aborted or terminates abnormally
#PBS -m n
### Number of nodes
#PBS -l nodes=1:thinnode:ppn=1
### Memory
#PBS -l mem=1gb
### Requesting time - format is <days>:<hours>:<minutes>:<seconds> (here, 12 hours)
#PBS -l walltime=00:00:15

# Go to the directory from where the job was submitted (initial directory is $HOME)
workdir=/home/projects/ku_00273/people/lardam/job_test/
echo Working directory is $workdir
cd $workdir

### Here follows the user commands:
# Define number of processors
NPROCS=$(wc -l < $PBS_NODEFILE)
echo This job has allocated $NPROCS nodes

# Load all required modules for the job
module load tools
module load anaconda3/4.4.0

source activate cenv

# This is where the work is done
#python test_job.py
#python get_file.py

conda deactivate

qsub jscript_2.sh
