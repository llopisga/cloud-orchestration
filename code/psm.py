#!/usr/bin/python3
# coding=utf-8
"""
Description: 
    - The current Python program is responsible for validating that the data entered complies with the screening, selection and scheduling policies, in that same order.
"""
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

import os
import yaml
import random
import logging
from emailClient import sendEmail
from subprocess import check_output
from datetime import datetime, timedelta

with open("./conf/config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = config['SMTP_PORT']
FROM = config['NOTIFY_ADMIN']
AUTH_USER = os.environ['MAIL_USERNAME']
AUTH_TOKEN = os.environ['MAIL_TOKEN']

PSM_FEASIBLES = dict()      # Feasible PSM's Model data
SCREENING_DATA = dict()     # Screening policy data
SELECTION_DATA = dict()     # Selection policy data
SCHEDULING_DATA = dict()    # Scheduling policy data
NOTIFY_USER = []            # An array of string validations

class policies:
    def __init__(self, UUID, PROJECT_PATH):
        self.UUID = UUID
        self.PROJECT_PATH = PROJECT_PATH

    def openPSModel(self):
        """
        Opens feasibles PSM YAML file previously generated
        """
        global op_mode, duration, start_date, feasiblesPSM, feasiblesNodes, PIMarray, PSM_OUTPUT
        PIMarray, feasiblesPSM, feasiblesNodes = [], [], []
        PSM_OUTPUT = str(self.PROJECT_PATH) + '/production/requests/PSM-' + self.UUID + '.yaml'
        PSM_REQUEST = str(self.PROJECT_PATH) + '/PSM/requests/PSMrequest-' + self.UUID + '.yaml'
        with open(PSM_REQUEST, 'r') as PIMfile:
            for key, value in yaml.full_load(PIMfile).items():
                if (key != 'system'):
                    PSM_FEASIBLES.update({key: value})

        op_mode = [k for k in PSM_FEASIBLES['operation_mode']][0]
        for x in PSM_FEASIBLES['operation_mode'][op_mode]:
            if (x == 'defined'):
                duration = PSM_FEASIBLES['operation_mode'][op_mode][x]['duration']
                start_date = PSM_FEASIBLES['operation_mode'][op_mode][x]['start_date']
                break
            duration = x

        [feasiblesPSM.append(x) for x in PSM_FEASIBLES['PSM_FEASIBLESs']]
        [feasiblesNodes.append(x) for x in PSM_FEASIBLES['NODES_FEASIBLESs']]

        PIMarray.append(PSM_FEASIBLES['machine_size'])
        PIMarray.append(PSM_FEASIBLES['lesson_type'])

    def openPolicies(self):
        """
        Opens policies files
        """
        with open(str(self.PROJECT_PATH) + '/repositories/policies/screening.yaml', 'r') as policyfile:
            for key, value in yaml.full_load(policyfile).items():
                SCREENING_DATA.update({key: value})

        with open(str(self.PROJECT_PATH) + '/repositories/policies/selection.yaml', 'r') as policyfile:
            for key, value in yaml.full_load(policyfile).items():
                SELECTION_DATA.update({key: value})

        with open(str(self.PROJECT_PATH) + '/repositories/policies/scheduling.yaml', 'r') as policyfile:
            for key, value in yaml.full_load(policyfile).items():
                SCHEDULING_DATA.update({key: value})

    def time_difference(self, time_start):
        """
        Check time difference between service start date and current date
        """
        diff = datetime.strptime(time_start, '%d-%m-%Y') - datetime.now()
        return diff.days

    def screening(self):
        """
        Screening policy: If any data invalid, then it adds string to NOTIFY_USER array
        """
        global NOTIFY_USER, durationUndefined, start_date
        for key in SCREENING_DATA:
            if (key == 'min-time-before-start'):
                try:
                    if (duration != 'undefined'):
                        if (self.time_difference(start_date) < SCREENING_DATA[key]):
                            NOTIFY_USER.append('The start date must be greater than or equal to ' + str(SCREENING_DATA[key]) + ' day.')
                    else:
                        tmp = datetime.now() + timedelta(days=SCREENING_DATA[key])
                        start_date = tmp.strftime('%d-%m-%Y')
                except:
                    pass
            elif (key == 'minimums'):
                try:
                    screeningPol = SCREENING_DATA[key][PSM_FEASIBLES['teacher_role']][PSM_FEASIBLES['machine_size']]
                    for x in screeningPol:
                        if (duration != 'undefined'):
                            if (x == 'availability' and screeningPol[x] > int(duration)):
                                NOTIFY_USER.append('Minimums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', duration must be greater than ' + str(screeningPol['availability']) + ' days.')
                            elif (x == 'users' and screeningPol[x] > len(PSM_FEASIBLES['users'])):
                                NOTIFY_USER.append('Minimums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', number of users must be greater than ' + str(screeningPol['users']) + '.')
                            elif (x == 'groups' and screeningPol[x] > len(PSM_FEASIBLES['user_cooperation_mode']['groups'])):
                                NOTIFY_USER.append('Minimums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', number of groups must be greater than ' + str(screeningPol['groups']) + '.')
                        else:
                            minimum = screeningPol['availability']
                except:
                    pass

            elif (key == 'maximums'):
                try:
                    screeningPol = SCREENING_DATA[key][PSM_FEASIBLES['teacher_role']][PSM_FEASIBLES['machine_size']]
                    for x in screeningPol:
                        if (duration != 'undefined'):
                            if (x == 'availability' and screeningPol[x] < int(duration)):
                                NOTIFY_USER.append('Maximums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', duration must be smaller than ' + str(screeningPol['availability']) + ' days.')
                        else:
                            maximum = screeningPol['availability']
                        if (x == 'users' and screeningPol[x] < len(PSM_FEASIBLES['users'])):
                            NOTIFY_USER.append('Maximums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', number of users must be smaller than ' + str(screeningPol['users']) + '.')
                        elif (x == 'groups' and screeningPol[x] < len(PSM_FEASIBLES['user_cooperation_mode']['groups'])):
                            NOTIFY_USER.append('Maximums policy not satisfied by ' + PSM_FEASIBLES['teacher_role'] + ', number of groups must be smaller than ' + str(screeningPol['groups']) + '.')

                except:
                    pass

        if (duration == 'undefined'):
            durationUndefined = random.randrange(minimum, maximum+1, 5)

    def nodesHealth(self, DESTHOST):
        """
        Gets the Memory Available status of every feasible node
        """
        HOST_UP = True if os.system("ping -c 1 " + DESTHOST + " > /dev/null") == 0 else False
        if (HOST_UP == True):
            USERNAME = os.getenv('USER')
            status = {'CPUusage': "echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')]",
                      'MemAvailable': 'cat /proc/meminfo | grep MemAvailable'}
            for x in status:
                tmp = check_output(["ssh", USERNAME + "@" + DESTHOST, status[x]]).decode("utf-8")
                value = int(tmp.strip(x + ':').strip().strip(' kB'))
                value //= 1024
                status.update({x: value})
        else:
            status = {DESTHOST: 'down'}
        return status

    def selection(self):
        """
        Selects the best PSM and Node of all feasibles
        """
        global bestPSM, bestNode
        matchPSM = {}
        counter = 0
        for psm in feasiblesPSM:
            for key in SELECTION_DATA:
                if (key == 'psm'):
                    for rule in SELECTION_DATA[key]:
                        if (rule == psm):
                            for x in SELECTION_DATA[key][rule]:
                                for i in SELECTION_DATA[key][rule][x]:
                                    if i in PIMarray:
                                        counter += 1
            matchPSM.update({psm: counter})
            counter = 0
        bestPSM = max(matchPSM, key=matchPSM.get)
        #print('Selected PSM is ' + bestPSM)

        matchNode = {}
        for node in feasiblesNodes:
            nodeDict = self.nodesHealth(node)
            if node in nodeDict:
                print("Node " + node + " is down.")
            else:
                matchNode.update({node: nodeDict['MemAvailable']})


        # Node - total ram in that node reserved
        bestNode = 'node01'
        #bestNode = max(matchNode, key=matchNode.get)
        #print('Selected Node is ' + bestNode)
        
    def validation(self):
        """
        Validate if NOTIFY_USER contains any invalid data and send mail to requester.
        """
        successSubject = 'Teacher request completed'
        successMessage = "" 'Dear ' + PSM_FEASIBLES['firstname'] + ',\n\nI am writing to inform you that your request has been processed in the system as identifier ' + self.UUID + ', please save this identifier.\n\nYours sincerely,\nMEC Admin'

        invalid = ""
        for i in NOTIFY_USER:
            invalid += '- ' + i + '\n\t'
        modSubject = 'Modify teacher request'
        modMessage = "" 'Dear ' + PSM_FEASIBLES['firstname'] + ',\n\nI regret to inform you that some data of your request with identifier ' + self.UUID + ' is not valid, this are the causes:\n\t' + invalid + '\nPlease, request again the service by entering your ID ('+PSM_FEASIBLES['requestor_id'] + ') and Modify as Operation Mode in order to edit the data following the previous instructions.\nYours sincerely,\nMEC Admin'

        delSubject = 'Delete teacher request'
        delMessage = "" 'Dear ' + PSM_FEASIBLES['firstname'] + ',\n\nI inform you that your request with identifier ' + self.UUID + ' is has been processed and it is going to be deleted.\n\nYours sincerely,\nMEC Admin'

        if (not NOTIFY_USER and not op_mode == 'delete'):
            print('All requested data has been verified and it is correct.')
            sendEmail(SMTP_SERVER, SMTP_PORT, FROM, PSM_FEASIBLES['requestor_email'], successSubject, successMessage, AUTH_USER, AUTH_TOKEN).send()
        elif (NOTIFY_USER):
            print('Some data needs to be modified.')
            sendEmail(SMTP_SERVER, SMTP_PORT, FROM, PSM_FEASIBLES['requestor_email'], modSubject, modMessage, AUTH_USER, AUTH_TOKEN).send()
            os._exit(1)
        elif (op_mode == 'delete'):
            print('Processing deletion request.')
            sendEmail(SMTP_SERVER, SMTP_PORT, FROM, PSM_FEASIBLES['requestor_email'], delSubject, delMessage, AUTH_USER, AUTH_TOKEN).send()

    def scheduling(self):
        """
        Schedules service request with a priority
        """
        schedulePath = self.PROJECT_PATH + '/production/preempt/'
        pattern = 'preempt-'
        listFiles = [f for f in os.listdir(schedulePath) if f.startswith(pattern)]
        priorities = []
        try:
            for p in listFiles:
                with open(schedulePath + p, 'r') as conversionfile:
                    for key, value in yaml.full_load(conversionfile).items():
                        [priorities.append(value[x]) for x in value if x == 'priority']
                                
            priority = max(priorities) + 1
        except:
            priority = 0
        
        preemptData = dict(
            preempt=dict(
                uuid=self.UUID,
                priority=priority,
                destination=bestNode,
                state='ready',
                arrival_time=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                start_date=start_date
            )
        )

        with open(schedulePath + 'preempt-' + self.UUID + '.yaml', 'w') as outfile:
            yaml.dump(preemptData, outfile, default_flow_style=False)

    def prodPSModel(self):
        """
        Production PSM YAML file based on policies results.
        """
        global finalPSM
        finalPSM = dict()
        for key in PSM_FEASIBLES:
            if (key == 'PSM_FEASIBLESs'):
                for i in PSM_FEASIBLES[key]:
                    if (i == bestPSM):
                        tmp = {i: PSM_FEASIBLES[key][i]}
                        finalPSM.update({'service': tmp})
            elif (key == 'NODES_FEASIBLESs'):
                for i in PSM_FEASIBLES[key]:
                    if (i == bestNode):
                        tmp = {i: PSM_FEASIBLES[key][i]}
                        finalPSM.update({'server': tmp})
            else:
                finalPSM.update({key: PSM_FEASIBLES[key]})

        finalPSM.update({'timestamp_completed': datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        if (duration == 'undefined'):
            finalPSM['operation_mode'][op_mode][duration] = {'start_date': start_date, 'duration': durationUndefined}

        with open(PSM_OUTPUT, 'w') as outfile:
            yaml.dump(finalPSM, outfile, default_flow_style=False)

    def delete(self):
        '''
        Replace Operation Mode to delete in production PSM
        '''
        global bestNode, start_date
        fin = open(PSM_OUTPUT, "rt")
        data = fin.read()
        data = data.replace('create', 'delete')
        data = data.replace('modify', 'delete')
        fin.close()
        fin = open(PSM_OUTPUT, "wt")
        fin.write(data)
        fin.close()

        with open(PSM_OUTPUT, 'r') as PIMfile:
            PIM = yaml.full_load(PIMfile)
            for key, value in PIM.items():
                if (key == 'server'):
                    for k in value:
                        bestNode = k

        start_date = datetime.now().strftime("%d-%m-%Y")

    def main(self):
        LOG_NAME = self.PROJECT_PATH + '/logs/log_' + self.UUID + '.log'
        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(LOG_NAME)
        f_handler.setLevel(logging.WARNING)
        f_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(message)s'))
        logger.addHandler(f_handler)

        logger.warning('Opening PSM Feasibles')
        self.openPSModel()
        
        if (op_mode != 'delete'):
            logger.warning('Opening Policies')
            self.openPolicies()
            logger.warning('Applying Screening policy')
            self.screening()
            logger.warning('Applying Selection policy')
            self.selection()
            logger.warning('Validating data')
            self.validation()
            logger.warning('Applying Scheduling policy')
            self.scheduling()
            logger.warning('Writing production PSM')
            self.prodPSModel()
            logger.warning('Model Orchestrator has finished')
        else:
            logger.warning('Processing deletion')
            self.delete()
            logger.warning('Validating deletion')
            self.validation()
            logger.warning('Scheduling deletion')
            self.scheduling()
