#!/bin/bash
# Steps:
#       http://tljh.jupyter.org/en/latest/contributing/dev-setup.html?highlight=dev

# exit when any command fails
set -e

trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT


# The main variables are assigned using the arguments of the code call
DEPLOYPATH=$1
LESSON=$2
TYPE=$3

# Change directory to the antidote-selfmedicate path
cd $DEPLOYPATH

# If the main Jupyter code is not present, then clone it
if [ ! -d "the-littlest-jupyterhub" ]
then
    git clone https://github.com/jupyterhub/the-littlest-jupyterhub.git
fi

# Jump to the Jupyter code directory
cd the-littlest-jupyterhub/

# Build the docker image and run it with variables
docker build -t tljh-systemd . -f integration-tests/Dockerfile
docker run --privileged --detach --name=JUPYTER_VMNAME --publish JUPYTER_PORT:80 --mount type=bind,source=$(pwd),target=/srv/src tljh-systemd
# After being created, first execute the installation and then set resources limits
docker exec -t JUPYTER_VMNAME python3 /srv/src/bootstrap/bootstrap.py --admin admin:JUPYTER_PASSWORD
docker exec -t JUPYTER_VMNAME sudo tljh-config set limits.memory JUPYTER_MEMORYM
docker exec -t JUPYTER_VMNAME sudo tljh-config set limits.cpu JUPYTER_CPUS

# For N users requested, create them in the system
for i in {1..JUPYTER_USERS}
do
    docker exec -t JUPYTER_VMNAME sudo tljh-config add-item users.allowed user$i
done

# Future work: All info in tljh/configurer.py
# Add collaboration modes
#if groups:
    #docker exec -t JUPYTER_VMNAME sudo tljh-config set users.extra_user_groups.group1 user1

# Reload all applied config in TLJH
docker exec -t JUPYTER_VMNAME sudo tljh-config reload

# Clone the selected lesson in the shared folder under /home
docker exec -t JUPYTER_VMNAME git clone $LESSON /home/shared/$TYPE

# Add designed port to firewall exception
sudo firewall-cmd --permanent --add-port=JUPYTER_PORT/tcp
sudo firewall-cmd --reload

# Change working directory to the parent deploy directory
cd $DEPLOYPATH

# Create the instructions for the teacher if the service deployment succeeds
echo "The service with UUID JUPYTER_VMNAME, is ready at URL $(eval "hostname -i"):JUPYTER_PORT." >> completed.txt
echo "Administrator credentials:" >> completed.txt
echo "Username: admin" >> completed.txt
echo "Password: JUPYTER_PASSWORD" >> completed.txt