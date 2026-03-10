#!/bin/bash

ip=$(hostname -I)
hostname=$(hostname)
HOMEPATH="/home/dassco"

echo $ip $hostname

ssh-keygen -t ed25519 -N "" -f $HOMEPATH/.ssh/slurm

cat $HOMEPATH/.ssh/slurm.pub