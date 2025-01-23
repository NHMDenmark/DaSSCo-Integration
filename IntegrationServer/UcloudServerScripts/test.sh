#!/bin/bash

ip=$(hostname -I)

echo $ip

sudo bash -c "source /home/ucloud/.bashrc && echo 'Changes applied'"
