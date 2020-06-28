#!/bin/bash
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

# Setting global variables to arguments
VMPROVIDER=$1
DEPLOYPATH=$2
UUID=$3
PORT=$4

# Go to the antidote-selfmedicate path
cd $DEPLOYPATH

if [ "$VMPROVIDER" == "virtualbox" ]; then
    # Size is equal to small, we are going to use Virtualbox


    command -v VBoxManage >/dev/null 2>&1 || { echo >&2 "I require VBoxManage but it's not installed.  Aborting."; exit 1; }
    command -v vagrant >/dev/null 2>&1 || { echo >&2 "I require vagrant but it's not installed.  Aborting."; exit 1; }
    
    # Change directory to antidote selfmedicate and run up the Vagrant provisioner.
    cd ./antidote-selfmedicate
    
    vagrant plugin install vagrant-vbguest
    vagrant plugin install vagrant-hostsupdater

elif [ "$VMPROVIDER" == "libvirt" ]; then
    # Size is equal to medium or large, we are going to use Docker

    command -v libvirtd >/dev/null 2>&1 || { echo >&2 "I require libvirtd but it's not installed.  Aborting."; exit 1; }
    command -v vagrant >/dev/null 2>&1 || { echo >&2 "I require vagrant but it's not installed.  Aborting."; exit 1; }
    
    cd ./antidote-selfmedicate

    vagrant plugin install vagrant-libvirt
    vagrant plugin install vagrant-hostsupdater

    #service libvirtd start

fi

# Generate output completion
#COMMAND='vagrant up 2> ./exited_error.txt
vagrant up

sudo firewall-cmd --permanent --add-port=$PORT/tcp
sudo firewall-cmd --reload

cd $DEPLOYPATH

echo "The service with UUID $UUID, is ready at URL antidote-local:$PORT." >> completed.txt
echo "Before accessing it, add this line:" >> completed.txt
echo "Linux: gedit /etc/hosts" >> completed.txt
echo "Windows: Open with Administrator privileges c:\Windows\System32\Drivers\etc\hosts" >> completed.txt
echo "" >> completed.txt
echo "In any case add this line:" >> completed.txt
echo "$(eval "hostname -i")    antidote-local" >> completed.txt