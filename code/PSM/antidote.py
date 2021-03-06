#!/usr/bin/python3
# coding=utf-8
"""
Description:
    - Antdiote (PSM) Python program responsible for generating the specific platform code.
"""
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

import os
import sys
import yaml
import socket
import shutil
import logging
import importlib
import logging.handlers
from datetime import datetime
from subprocess import Popen, PIPE, call

PSM_DATA = dict()       # Handles PSM data with all feasible PSM's
ANTIDOTE_DATA = dict()  # Handles the replacement data to map into a new Vagrant file

with open("./conf/config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

USER_NAME = os.getenv('USER')
PROJECT_PATH = config['PROJECT_PATH'].replace("USERNAME", USER_NAME)
SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = config['SMTP_PORT']
FROM = config['NOTIFY_ADMIN']
TO = [config['NOTIFY_ADMIN']]
MSG = 'Error handled!'
AUTH_USER = os.environ['MAIL_USERNAME']
AUTH_TOKEN = os.environ['MAIL_TOKEN']

PATH_CODE = str(PROJECT_PATH) + '/code/PSM/'
sys.path.append(PATH_CODE)
em = importlib.import_module('emailClient', package=None)

logger = logging.getLogger()
se = em.errorEmail((SMTP_SERVER, SMTP_PORT), FROM, TO, MSG, (AUTH_USER, AUTH_TOKEN))
se.setLevel(logging.ERROR)
logger.addHandler(se)

tmp = PROJECT_PATH.split('/')[-1].split('.')[0]
USER_PATH = PROJECT_PATH.replace(tmp, '')


class code:

    def __init__(self, UUID, PROJECT_PATH, PSM_NAME, VIRT_TECH, PSM_DATA):
        self.UUID = UUID
        self.PROJECT_PATH = PROJECT_PATH
        self.PSM_NAME = PSM_NAME
        self.VIRT_TECH = VIRT_TECH
        self.PSM_DATA = PSM_DATA

    def setVariables(self):
        """
        Gets most recent file in Production folder and gathers the UUID
        """
        global lessons_url, dstServer, startp, stopp

        lessons_url = self.PSM_DATA['service'][self.PSM_NAME]['lessons_url']
        startp = self.PSM_DATA['firewall_rules']['allow']['ports']['min']
        stopp = self.PSM_DATA['firewall_rules']['allow']['ports']['max']

        for x in self.PSM_DATA['server']:
            dstServer = self.PSM_DATA['server'][x]['network']['ip']

        ANTIDOTE_DATA.update(
            {'ANTIDOTE_VMNAME': self.PSM_DATA['request_UUID']})
        ANTIDOTE_DATA.update(
            {'ANTIDOTE_MEMORY': self.PSM_DATA['service'][self.PSM_NAME][self.VIRT_TECH]['memory']})
        ANTIDOTE_DATA.update(
            {'ANTIDOTE_CPUS': self.PSM_DATA['service'][self.PSM_NAME][self.VIRT_TECH]['cores']})
        ANTIDOTE_DATA.update(
            {'ANTIDOTE_PROVIDER': self.PSM_DATA['service'][self.PSM_NAME][self.VIRT_TECH]['provider']})

    def checkAvailablePorts(self):
        '''
        Check which ports are available in destination server
        '''
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_range = 1000
        for x in range(startp, stopp):
            location = (dstServer, x)
            result_of_check = a_socket.connect_ex(location)
            if not result_of_check == 0:
                ANTIDOTE_DATA.update({'ANTIDOTE_PORT': x})
                break
        for y in range(stopp+1, stopp+port_range):
            location = (dstServer, y)
            result_of_check = a_socket.connect_ex(location)
            if not result_of_check == 0:
                ANTIDOTE_DATA.update({'ANTIDOTE_TMP': y})
                break
        for z in range(startp-port_range, stopp-1):
            location = (dstServer, z)
            result_of_check = a_socket.connect_ex(location)
            if not result_of_check == 0:
                ANTIDOTE_DATA.update({'ANTIDOTE_SSH': z})
                break
        a_socket.close()

    def copyPSMcode(self):
        '''
        Copy and download necessary source code files from repository
        '''
        global DEPLOY_PATH
        REPO_PATH   = str(self.PROJECT_PATH) + '/PSM/repositories/' + self.PSM_NAME + '/'
        DEPLOY_PATH = str(self.PROJECT_PATH) + '/production/deploy/service_' + str(self.UUID) + '/'

        if not os.path.exists(DEPLOY_PATH):
            os.mkdir(DEPLOY_PATH)
        else:
            shutil.rmtree(DEPLOY_PATH, ignore_errors=True)
            
        call(["cp", "-a", REPO_PATH+".", DEPLOY_PATH])

        if (lessons_url != None):
            dirName, ext = (lessons_url.split('/')[-1].split('.'))  # get repo name
            call(["git", "clone", lessons_url, DEPLOY_PATH+dirName])

    def replaceVariables(self):
        '''
        Replace PSM production data in the code variables
        '''
        ANTIDOTE_DIR = str(DEPLOY_PATH) + 'antidote-selfmedicate/'
        arrayOfFiles = ['antidote-config.yml', 'selfmedicate.sh']
        for file in arrayOfFiles:
            fin = open(ANTIDOTE_DIR + file, "rt")
            data = fin.read()
            for i, j in ANTIDOTE_DATA.items():
                data = data.replace(i, str(j))
                fin.close()
                fin = open(ANTIDOTE_DIR + file, "wt")
                fin.write(data)
            fin.close()

    def main(self):
        try:
            self.setVariables()
            self.checkAvailablePorts()
            self.copyPSMcode()
            self.replaceVariables()
        except Exception:
            logger.exception('Unhandled Exception')




class deploy:

    def __init__(self, UUID, PROJECT_PATH, DEST_NODE, PSM_DATA):
        self.UUID = UUID
        self.PROJECT_PATH = PROJECT_PATH
        self.DEST_NODE = DEST_NODE
        self.PSM_DATA = PSM_DATA

    def copyFiles(self):
        '''
        Copy code directory created to destination server, not needed for this implementation.
        '''
        global SSH_NODE
        SSH_NODE = USER_NAME + "@" + self.DEST_NODE
        LOCAL_PATH = str(self.PROJECT_PATH) + "/production/deploy/service_" + self.UUID + "/"
       
        call(["scp", "-r", LOCAL_PATH, SSH_NODE + ":" + USER_PATH])

    def executeProvision(self):
        '''
        Execute provision.sh in destination node to bring up the service
        '''
        global DEPLOY_PATH
        DEPLOY_PATH = USER_PATH + "service_" + self.UUID + "/"
        command = 'chmod +x ' + DEPLOY_PATH + 'provision.sh'
        call(["ssh", SSH_NODE, command])
        command = "/bin/bash " + DEPLOY_PATH + "provision.sh " + str(ANTIDOTE_DATA['ANTIDOTE_PROVIDER']) + " " + DEPLOY_PATH + " " + str(ANTIDOTE_DATA['ANTIDOTE_VMNAME']) + " " + str(ANTIDOTE_DATA['ANTIDOTE_PORT']) + " >>" + DEPLOY_PATH + "logs/output.txt 2>&1"
        stdout, stderr = Popen(['ssh', SSH_NODE, command]).communicate()
        print(stdout)

    def notify(self):
        '''
        If the service is successfully deployed, then notify the techer with details in completed.txt
        '''
        REMOTE_COPY_PATH = DEPLOY_PATH + "completed.txt"
        PATH_CODE = str(self.PROJECT_PATH) + '/code'
        LOCAL_COPY_PATH = str(self.PROJECT_PATH) + "/production/deploy/service_" + self.UUID + "/completed.txt"

        sys.path.append(PATH_CODE)
        psm = importlib.import_module('emailClient', package=None)

        call(["scp", SSH_NODE + ":" + REMOTE_COPY_PATH, LOCAL_COPY_PATH])

        if (tmp):
            completedSubject = 'Service ' + self.UUID + ' available'
            completedMessage = 'Dear ' + self.PSM_DATA['firstname'] + ',\n\nI inform you that your service requested with UUID ' + \
                self.UUID + ' has been successfuly completed and it is available. Please find more details in the attached file.\nYours sincerely,\nMEC Admin'
            psm.sendComplete(SMTP_SERVER, SMTP_PORT, FROM, self.PSM_DATA['requestor_email'], completedSubject, completedMessage, AUTH_USER, AUTH_TOKEN, LOCAL_COPY_PATH).send()

    def main(self):
        try:
            self.copyFiles()
            self.executeProvision()
            self.notify()
        except Exception:
            logger.exception('Unhandled Exception')



class destroy:

    def __init__(self, UUID, PROJECT_PATH, DEST_NODE, PSM_DATA):
        self.UUID = UUID
        self.PROJECT_PATH = PROJECT_PATH
        self.DEST_NODE = DEST_NODE
        self.PSM_DATA = PSM_DATA

    def delete(self):
        # 1. SAVE ALL DATA IN DESTINATION SERVER
        # Future work

        # 2. Stop and destroy container
        SSH_NODE = USER_NAME + "@" + self.DEST_NODE
        DEPLOY_PATH = USER_PATH + "service_" + self.UUID + "/"

        command = "cd X && vagrant stop UUID"
        command_stop = "cd " + USER_PATH + "service_" + self.UUID + "/ && vagrant halt " + self.UUID
        stdout, stderr = Popen(['ssh', SSH_NODE, command_stop]).communicate()
        print(stdout)

        command_remove =  "cd " + USER_PATH + "service_" + self.UUID + "/ && vagrant destroy " + self.UUID
        stdout, stderr = Popen(['ssh', SSH_NODE, command_remove]).communicate()
        print(stdout)

        # Remove in destination server the service directory
        command_dir = "rm -rf " + DEPLOY_PATH
        stdout, stderr = Popen(['ssh', SSH_NODE, command_dir]).communicate()
        print(stdout)

    
    def notify(self):
        PATH_CODE = str(self.PROJECT_PATH) + '/code'

        sys.path.append(PATH_CODE)
        psm = importlib.import_module('emailClient', package=None)

        removedSubject = 'Service ' + self.UUID + ' destroyed'
        removedMessage = 'Dear ' + self.PSM_DATA['firstname'] + ',\n\nI inform you that your service with UUID ' + self.UUID + ' has been successfuly destroyed. Please find the user data stored in ' + self.PSM_DATA['home_directories'] + ' server.\nYours sincerely,\nMEC Admin'
        psm.sendEmail(SMTP_SERVER, SMTP_PORT, FROM, self.PSM_DATA['requestor_email'], removedSubject, removedMessage, AUTH_USER, AUTH_TOKEN).send()

    def main(self):
        pass
        #self.delete()
        #self.notify()