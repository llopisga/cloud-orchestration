#!/bin/bash
# Steps:
#       http://tljh.jupyter.org/en/latest/contributing/dev-setup.html?highlight=dev

# exit when any command fails
set -e

trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT


# Setting global variables to arguments
DEPLOYPATH=$1
LESSON=$2
TYPE=$3

# Go to the antidote-selfmedicate path
cd $DEPLOYPATH

# if dir not exists
if [ ! -d "the-littlest-jupyterhub" ]
then
    git clone https://github.com/jupyterhub/the-littlest-jupyterhub.git
fi
cd the-littlest-jupyterhub/

docker build -t tljh-systemd . -f integration-tests/Dockerfile
docker run --privileged --detach --name=JUPYTER_VMNAME --publish JUPYTER_PORT:80 --mount type=bind,source=$(pwd),target=/srv/src tljh-systemd
docker exec -t JUPYTER_VMNAME python3 /srv/src/bootstrap/bootstrap.py --admin admin:JUPYTER_PASSWORD

docker exec -t JUPYTER_VMNAME sudo tljh-config set limits.memory JUPYTER_MEMORYM
docker exec -t JUPYTER_VMNAME sudo tljh-config set limits.cpu JUPYTER_CPUS

for i in {1..JUPYTER_USERS}
do
    docker exec -t JUPYTER_VMNAME sudo tljh-config add-item users.allowed user$i
done

# Future work: All info in tljh/configurer.py
#if groups:
    #docker exec -t JUPYTER_VMNAME sudo tljh-config set users.extra_user_groups.group1 user1


docker exec -t JUPYTER_VMNAME sudo tljh-config reload

docker exec -t JUPYTER_VMNAME git clone $LESSON /home/shared/$TYPE
sudo firewall-cmd --permanent --add-port=JUPYTER_PORT/tcp
sudo firewall-cmd --reload


cd $DEPLOYPATH
echo "The service with UUID JUPYTER_VMNAME, is ready at URL $(eval "hostname -i"):JUPYTER_PORT." >> completed.txt
echo "Administrator credentials:" >> completed.txt
echo "Username: admin" >> completed.txt
echo "Password: JUPYTER_PASSWORD" >> completed.txt