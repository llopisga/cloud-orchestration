# Implementation

## Steps

### Master node
```
sudo yum update -y && sudo yum upgrade -y
sudo cat << EOF >> /etc/hosts
# Final Project hosts
172.26.91.18	master	www.thesisraul.mche.edu.pl
172.26.91.20 	node01
172.26.91.21	node02
EOF

sudo hostnamectl set-hostname master

sudo yum install -y epel-release yum-utils git curl php mysql-server python3 perl yaml php-pecl-yaml.x86_64 php-yaml php-mysqli pip3 pyyaml

sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=httpd
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

sudo usermod -aG apache raulloga

sudo systemctl enable httpd
sudo systemctl start httpd
sudo systemctl enable mysqld
sudo systemctl start mysqld

sudo chmod -R 700 .ssh/
sudo chmod -R 600 ~/.ssh/id_*
sudo chmod -R 600 ~/.ssh/authorized_keys

pip3 install --user pyyaml

sudo cat << EOF >> ~/.bash_profile
export MAIL_USERNAME=raullg8@gmail.com
export MAIL_TOKEN=smzydybjsizonmca
EOF
source ~/.bash_profile



```

### Nodes
```
sudo yum update -y && sudo yum upgrade -y
sudo vi /etc/hosts
sudo hostnamectl set-hostname master

sudo yum install -y epel-release yum-utils git curl python3 gcc dkms make qt libgomp patch kernel-headers kernel-devel binutils glibc-headers glibc-devel font-forge dkms

yum install qemu-kvm libvirt libvirt-python libguestfs-tools virt-install

sudo yum groupinstall "Cinnamon Desktop"
systemctl set-default graphical
reboot

sudo yum check-update
curl -fsSL https://get.docker.com/ | sh
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $(whoami)

sudo wget https://releases.hashicorp.com/vagrant/2.2.2/vagrant_2.2.2_x86_64.rpm
sudo rpm -i vagrant_2.2.2_x86_64.rpm

sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=httpd
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

sudo usermod -aG apache raulloga

sudo systemctl enable httpd
sudo systemctl start httpd
sudo systemctl enable mysqld
sudo systemctl start mysqld

sudo chmod -R 700 .ssh/
sudo chmod -R 600 ~/.ssh/id_*
sudo chmod -R 600 ~/.ssh/authorized_keys

```


### VirtualBox
```
VBoxManage list vms
VBoxManage list runningvms
VBoxManage startvm <UUID>
VBoxManage controlvm <UUID> poweroff
VBoxManage unregistervm --delete <UUID>
```

#### Enable Virtualization on VBox
```
VBoxManage modifyvm virtualbox-name --nested-hw-virt on
```

#### Errors
```
VBoxManage dhcpserver remove --netname HostInterfaceNetworking-vboxnet1
```

#### Stop all running machines
```
VBoxManage list runningvms | awk '{print $2;}' | xargs -I vmid VBoxManage controlvm vmid poweroff
```

#### Delete all machines
```
VBoxManage list vms | awk '{print $2;}' | xargs -I vmid VBoxManage unregistervm --delete vmid
```

### docker
```
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io

sudo systemctl enable docker
sudo systemctl start docker
sudo docker run hello-world
sudo usermod -aG docker raulloga

```
