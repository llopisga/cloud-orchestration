#!/bin/bash
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

# The main variables are assigned using the arguments of the code call
VMPROVIDER=$1
DEPLOYPATH=$2
UUID=$3
PORT=$4

# Change directory to the antidote-selfmedicate path
cd $DEPLOYPATH

# In this implementation, libvirt has not been introduced, although work has been done so the code is left.

if [ "$VMPROVIDER" == "virtualbox" ]; then
    # If the provider is Virtualbox
     
    # Check if Virtualbox and vagrant are installed. Abort if not.
    command -v VBoxManage >/dev/null 2>&1 || { echo >&2 "I require VBoxManage but it's not installed.  Aborting."; exit 1; }
    command -v vagrant >/dev/null 2>&1 || { echo >&2 "I require vagrant but it's not installed.  Aborting."; exit 1; }
    
    # Change directory to antidote selfmedicate and install needed plugins
    cd ./antidote-selfmedicate
    
    vagrant plugin install vagrant-vbguest
    vagrant plugin install vagrant-hostsupdater

elif [ "$VMPROVIDER" == "libvirt" ]; then
    # If the provider is Libvirt

    # Check if Libvirt and vagrant are installed. Abort if not.
    command -v libvirtd >/dev/null 2>&1 || { echo >&2 "I require libvirtd but it's not installed.  Aborting."; exit 1; }
    command -v vagrant >/dev/null 2>&1 || { echo >&2 "I require vagrant but it's not installed.  Aborting."; exit 1; }
    
    cd ./antidote-selfmedicate

    vagrant plugin install vagrant-libvirt
    vagrant plugin install vagrant-hostsupdater

fi

# Be sure to be in Antidote dir and perform the deployment of the Antidote code
cd ./antidote-selfmedicate
vagrant up

# Add designed port to firewall exception
sudo firewall-cmd --permanent --add-port=$PORT/tcp
sudo firewall-cmd --reload

# Change working directory to the parent deploy directory
cd $DEPLOYPATH

# Create the instructions for the teacher if the service succeeds
echo "The service with UUID $UUID, is ready at URL antidote-local:$PORT." >> completed.txt
echo "Before accessing it, add this line:" >> completed.txt
echo "Linux: gedit /etc/hosts" >> completed.txt
echo "Windows: Open with Administrator privileges c:\Windows\System32\Drivers\etc\hosts" >> completed.txt
echo "" >> completed.txt
echo "In any case add this line:" >> completed.txt
echo "$(eval "hostname -i")    antidote-local" >> completed.txt