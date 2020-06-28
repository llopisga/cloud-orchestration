#!/usr/bin/env bash

# Change user context to the desired user, the call to this script is made by apache user in request.php
USR_CONTEXT='raulloga'

sudo -i -u $USR_CONTEXT bash << EOF
cd /home/$USR_CONTEXT/cloud-orchestration/code
chmod +x ./orchestrator.py
python3 ./orchestrator.py $1
EOF
