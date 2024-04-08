
#!/bin/sh

#PBS -W group_list=ku_00273 -A ku_00273

#PBS -N script_2
#PBS -m n
### Number of nodes
#PBS -l nodes=1:thinnode:ppn=1
### Memory
#PBS -l mem=10m
### Requesting time - format is <days>:<hours>:<minutes>:<seconds> (here, 12 hours)
#PBS -l walltime=00:00:15

# Go to the directory from where the job was submitted (initial directory is $HOME)
workdir=/home/projects/ku_00273/people/lardam/job_test/
echo Working directory is $workdir
cd $workdir

# Load all required modules for the job
module load tools
module load anaconda3/4.4.0

python second_test_python.py
