# Source Code

Main code repository where the different processes are executed to create the service on demand.

## Structure

- conf
  - config.yaml: Setting parameters about the environment

- emailClient: Interface used to send three types of emails to the administrator and teachers.

- orchestrator: Model orchestrator
- pim: Platform Independent Model
- feasibles: Feasible Node and PSM Generator
- psm: Platform Specific Model

- service: Platform Orchestrator
- PSM
  - antidote: Specific code for build and deploy Antidote
  - jupyter: Specific code for build and deploy Jupyter


## Dependencies:
 - Install YAML module for Python
   ```
   pip install pyyaml
   ```