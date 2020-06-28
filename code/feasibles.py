#!/usr/bin/python3
# coding=utf-8
"""
Description:
    - The present Python program is responsible for converting the PIM file
    generated previously into a Feasibles Platform Specific Models (PSM) YAML file.
"""
import logging
import yaml
import os
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

PIM_DATA = dict()               # Handles PIM data
PSM_FEASIBLES = dict()          # Handles feasibles PSMs final data
NODES_FEASIBLES = dict()        # Handles feasibles Nodes final data
INVENTORY_PSM_DATA = dict()     # Handles Inventory PSM data
INVENTORY_NODES_DATA = dict()   # Handles Inventory Node data

class feasiblesPSM:
    def __init__(self, UUID, PROJECT_PATH):
        self.UUID = UUID
        self.PROJECT_PATH = PROJECT_PATH

    def openPIModel(self):
        """
        Opens PIM YAML file previously generated.
        """
        global machinesize, lessontype, lessontopic, vt, opsys, ram, storage, vcpu, PSM_OUTPUT, op_mode
        PSM_OUTPUT = str(self.PROJECT_PATH) + '/PSM/requests/PSMrequest-' + self.UUID + '.yaml'
        PIM_PATH = str(self.PROJECT_PATH) + '/PIM/requests/PIMrequest-' + self.UUID + '.yaml'
        with open(PIM_PATH, 'r') as PIMfile:
            for key, value in yaml.full_load(PIMfile).items():
                PIM_DATA.update({key: value})

        op_mode = [k for k in PIM_DATA['operation_mode']][0]
        machinesize = PIM_DATA['machine_size']
        lessontype = PIM_DATA['lesson_type']
        lessontopic = PIM_DATA['lesson_topic']
        vt = PIM_DATA['system']['vt']
        opsys = PIM_DATA['system']['os']
        ram = PIM_DATA['system']['ram']
        storage = PIM_DATA['system']['storage']
        vcpu = PIM_DATA['system']['vcpu']

    def inventoryPSM(self):
        """
        Opens PSM Inventory files for gathering values and generate PSM model based on templates
        """
        global PSM_FEASIBLES
        conversionDict, tmp, feasibles = {}, {}, []
        inventoryPath = self.PROJECT_PATH + '/repositories/inventory/psm/'
        pattern = "PSM_"
        listFiles = [f for f in os.listdir(inventoryPath) if f.startswith(pattern)]

        for psm in listFiles:
            with open(inventoryPath + psm, 'r') as conversionfile:
                convert = yaml.full_load(conversionfile)
                for key, value in convert.items():
                    INVENTORY_PSM_DATA.update({key: value})
                    for k in value:
                        for x in value[k]:
                            if (x == lessontype):
                                for y in value[k][x]:
                                    if (y == lessontopic):
                                        # Selects feasibles PSM based on Lesson Topic
                                        feasibles.append(key)

        for key in INVENTORY_PSM_DATA:  # From feasibles, gather it's data
            if key in feasibles:
                for i in INVENTORY_PSM_DATA[key]:
                    for x in INVENTORY_PSM_DATA[key][i]:
                        if (x == lessontype):
                            for y in INVENTORY_PSM_DATA[key][i][x]:
                                if (y == lessontopic):
                                    tmp.update(
                                        {'lessons_url': INVENTORY_PSM_DATA[key][i][x][y]})
                        elif (x == machinesize):
                            tmp.update(INVENTORY_PSM_DATA[key][i][x])
                conversionDict[key] = dict(tmp)
                tmp = {}

        PSM_FEASIBLES = dict(
            PSM_FEASIBLESs=conversionDict
        )

    def inventoryNodes(self):
        """
        Opens Node Inventory files for gathering values
        """
        global NODES_FEASIBLES
        counter, matching = 0, {}
        inventoryPath = self.PROJECT_PATH + '/repositories/inventory/nodes/'
        pattern = "node_"
        listFiles = [f for f in os.listdir(inventoryPath) if f.startswith(pattern)]

        for node in listFiles:
            with open(inventoryPath + node, 'r') as conversionfile:
                convert = yaml.full_load(conversionfile)
                for key, value in convert.items():
                    INVENTORY_NODES_DATA.update({key: value})
                    if (value['specs']['vcpu'] > vcpu):
                        counter += 1
                    if (value['specs']['ram'] > ram):
                        counter += 1
                    if (value['specs']['os'] == opsys):
                        counter += 1
                    if (value['specs']['vt'] == vt):
                        counter += 1
                    if (value['specs']['storage'] > storage):
                        counter += 1
                    matching.update({key: counter})
        feasiblesNodes = {}
        for i in matching:
            if (matching[i] >= 4):
                feasiblesNodes.update({i: INVENTORY_NODES_DATA[i]})

        NODES_FEASIBLES = dict(
            NODES_FEASIBLESs=feasiblesNodes
        )

        with open(PSM_OUTPUT, 'w') as outfile:
            yaml.dump(PIM_DATA, outfile, default_flow_style=False)
            yaml.dump(PSM_FEASIBLES, outfile, default_flow_style=False)
            yaml.dump(NODES_FEASIBLES, outfile, default_flow_style=False)

    def delete(self):
        fin = open(PSM_OUTPUT, "rt")
        data = fin.read()
        data = data.replace('create', 'delete')
        data = data.replace('modify', 'delete')
        fin.close()
        fin = open(PSM_OUTPUT, "wt")
        fin.write(data)
        fin.close()

    def main(self):
        LOG_NAME = self.PROJECT_PATH + '/logs/log_' + self.UUID + '.log'
        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(LOG_NAME)
        f_handler.setLevel(logging.WARNING)
        f_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(message)s'))
        logger.addHandler(f_handler)

        logger.warning('Opening PIM Model')
        self.openPIModel()
        
        if (op_mode != 'delete'):
            logger.warning('Opening PSM Inventories')
            self.inventoryPSM()
            logger.warning('Opening Nodes Inventories')
            self.inventoryNodes()
        else:
            logger.warning('Processing deletion')
            self.delete()
