#!/bin/bash

root="/work/data/Dev-Integration/DaSSCo-Integration/IntegrationServer"

path="$1"

nohup python "${root}/${path}" > "${root}/${path}.out" 2>&1 &