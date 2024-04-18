#!/bin/sh

#PBS -W group_list=ku_00273 -A ku_00273

#PBS -N loop
### Output files (comment out the next 2 lines to get the job name used instead)
#PBS -e loop.err
#PBS -o loop.log
### Only send mail when job is aborted or terminates abnormally
#PBS -m n
### Number of nodes
#PBS -l nodes=1:thinnode:ppn=1
### Memory
#PBS -l mem=1gb
### Requesting time - format is <days>:<hours>:<minutes>:<seconds>
#PBS -l walltime=00:05:00

workdir=/home/projects/ku_00273/people/lardam/job_test/
echo Working directory is $workdir
cd $workdir

# Load all required modules for the job
module load tools
module load anaconda3/4.4.0

# activate the conda environment
source activate cenv

# ensure env variables are available
if ! grep -qxF 'export APIBOOL=' ~/.bashrc; then
    echo 'export APIBOOL=True' >> ~/.bashrc
fi

# update the env variables
source ~/.bashrc

keep_running=true

# Run a while loop
while $keep_running; do
    # Run Python script and capture its output
    #output=$(python get_bool_from_api.py)
    
    # Wait for the Python script to finish executing
    #wait
    
    qsub bool_from_api_job.sh
    
    sleep 20  # Wait for x seconds before running the script again, asked for in computerome best practices

    source ~/.bashrc

    # Check the output of the Python script
    if [ $APIBOOL = "True" ]; then
        keep_running=true
    else
        keep_running=false
    fi
    
    
    echo $APIBOOL
done

conda deactivate