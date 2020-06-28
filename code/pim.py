#!/usr/bin/python3
# coding=utf-8
"""
Description:
    - The present Python module is responsible for converting the teacher's
    request (TM) into a Platform Independent Model (PIM) YAML file.
"""
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

import os
import yaml
import logging
from datetime import datetime

TM_DATA = dict()            # Handles TM request data in a dictionary
PIM_DATA = dict()           # Handles all PIM data
CONVERSION_DATA = dict()    # Handles conversion policy data


class conversionPIM:
    def __init__(self, UUID, TM_PATH, PROJECT_PATH):
        self.UUID = UUID
        self.TM_PATH = TM_PATH
        self.PROJECT_PATH = PROJECT_PATH

    def openTM(self):
        """
        Opens th Teacher Model YAML file generated from the web form and keeps relevant data
        """
        global teacher, machinesize, operationmode, lessontype, cooperationmode, persisted_dir
        TM_REQUEST = self.TM_PATH + '/TMrequest-' + self.UUID + '.yaml'
        with open(TM_REQUEST, 'r') as TMfile:
            for key, value in yaml.full_load(TMfile).items():
                TM_DATA.update({key: value})
        
        cooperationmode = [k for k in TM_DATA['user_cooperation_mode']][0]
        operationmode = [k for k in TM_DATA['operation_mode']][0]
        persisted_dir = TM_DATA['home_directories']
        machinesize = TM_DATA['machine_size']
        lessontype = TM_DATA['lesson_type']
        teacher = TM_DATA['teacher_role']

    def openConversion(self):
        """
        Opens Conversion templates and puts all data into a common dictionary.
        """
        templatesPath = self.PROJECT_PATH + '/repositories/templates/'
        pattern = "PIM_"
        listFiles = [f for f in os.listdir(templatesPath) if f.startswith(pattern)]

        for pim in listFiles:
            with open(templatesPath + pim, 'r') as conversionfile:
                [CONVERSION_DATA.update({key: value}) for key, value in yaml.full_load(conversionfile).items()]

    def generatePIM(self):
        """
        Generates PIM model based on previous loaded templates.
        """
        global PIM_DATA
        PIM_OUTPUT = self.PROJECT_PATH + '/PIM/requests/PIMrequest-' + self.UUID + '.yaml'
        if (operationmode == 'delete'):  # Think about it
            fin = open(PIM_OUTPUT, "rt")
            data = fin.read()
            data = data.replace('create', 'delete')
            data = data.replace('modify', 'delete')
            fin.close()
            fin = open(PIM_OUTPUT, "wt")
            fin.write(data)
            fin.close()
        elif (operationmode == 'create' or operationmode == 'modify'):
            
            for key in CONVERSION_DATA:

                for x in CONVERSION_DATA[key]:
                    if (x == lessontype):
                        systemDict = dict(CONVERSION_DATA[key][x][machinesize])
                    elif (x == cooperationmode):
                        privilegesDict = dict(CONVERSION_DATA[key][x][teacher])
                    elif (x == 'protocol'):
                        configDict = dict(CONVERSION_DATA[key][x]['dynamic'])
                    elif (x == 'action'):
                        firewallDict = dict(CONVERSION_DATA[key][x])
                    elif (x == 'where'):
                        persistDict = dict([('url', CONVERSION_DATA[key][x][persisted_dir])])

            PIM_DATA = dict(
                system=systemDict,
                privileges=privilegesDict,
                network_config=configDict,
                firewall_rules=firewallDict,
                persisted_items=persistDict
            )

            with open(PIM_OUTPUT, 'w') as outfile:
                yaml.dump(TM_DATA, outfile, default_flow_style=False)
                yaml.dump(PIM_DATA, outfile, default_flow_style=False)

    def main(self):
        LOG_NAME = self.PROJECT_PATH + '/logs/log_' + self.UUID + '.log'
        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(LOG_NAME)
        f_handler.setLevel(logging.WARNING)
        f_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(message)s'))
        logger.addHandler(f_handler)
        logger.warning('Model Orchestrator has started')

        logger.warning('Opening TM Model')
        self.openTM()
        logger.warning('Opening Conversion policies')
        self.openConversion()
        logger.warning('Generating PIM Model')
        self.generatePIM()
