#!/bin/bash

root="/work/integration/DaSSCo-Integration/IntegrationServer"

path="$1"
base_path="${path%.*}"  # removes the file extension

nohup python "${root}/${path}" > "${root}/${base_path}.out" 2>&1 &