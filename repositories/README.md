# Repositories

This is the directory of repositories where the most important YAML files for the behavior of the system are located. In this the following structure is presented.


Structure
--------

- Inventory
  - Nodes:  For each node in the system there will be a file with the data about the networking and resources.
  - PSM:    For each PSM in the system there will be a file with the data needed to apply the selection policy.
- Policies
  - Scheduling: For the current implementation this is not used, instead the FIFO queue is used in code/psm.py
  - Screening:  The validations on minimums and maximums allowed to the requests are specified.
  - Selection:  The characteristics of the PSM are specified to be chosen depending on the lesson type and machine size.
- Templates
  - Firewall:   Specifies the actions in the firewall of the system implemented, the range of ports is the most important.
  - Network:    Specifies characteristics of the network where the services will reside, by default it is dynamically assigned
  - Persistent: Specifies where the data will be saved by means of the link to the SFTP site
  - Privileges: Specify the privileges depending on the mode of cooperation and the teacher.
  - System:     Specifies resources for different system sizes based on the type of choice.
