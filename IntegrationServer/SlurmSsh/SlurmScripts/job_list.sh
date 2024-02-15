#!/bin/bash

job_list=$(squeue -r)

user="ldam01"

running_count=$(echo "$job_list" | grep -cE "$user\s+RUNNING")

pending_count=$(echo "$job_list" | grep -cE "$user\s+PENDING")

echo ""$running_count""
echo ""$pending_count""
echo "Total jobs running and pending: $(echo "$job_list" | wc -l)"
echo "Jobs running by user "$user": "$running_count" and jobs pending: "$pending_count""