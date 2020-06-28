#!/usr/bin/python3
# coding=utf-8
"""
Description: 
    - Platform Specific Orchestrator
"""
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

import os
import sys
import yaml
import time
import signal
import logging
import importlib
import logging.handlers
from datetime import datetime
from queue import PriorityQueue
from emailClient import errorEmail
from datetime import datetime, timedelta

start_time = time.time()

with open("./conf/config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

TM_PATH = config['TM_PATH']
PROJECT_PATH = config['PROJECT_PATH'].replace("USERNAME", os.getenv('USER'))
SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = config['SMTP_PORT']
FROM = config['NOTIFY_ADMIN']
TO = [config['NOTIFY_ADMIN']]
MSG = 'Error handled!'
AUTH_USER = os.environ['MAIL_USERNAME']
AUTH_TOKEN = os.environ['MAIL_TOKEN']

PREEMPT_PATH = str(PROJECT_PATH) + '/production/preempt/'
PSM_DIR = str(PROJECT_PATH) + '/production/requests/'
PATH_CODE = str(PROJECT_PATH) + '/code/PSM/'


def checkDuration():
    """
    Checks the end of the duration of the current PSM files.
    If some service it's about to end, it is added to the Priority Queue with 'delete' operation mode.
    """
    global duration
    pattern = 'PSM-'
    listFiles = [f for f in os.listdir(PSM_DIR) if f.startswith(pattern)]
    for p in listFiles:
        with open(PSM_DIR + p, 'r') as PSMfile:
            for key, value in yaml.full_load(PSMfile).items():
                if (key == 'request_UUID'):
                    req_uuid = value
                elif (key == 'server'):
                    for x in value:
                        bestNode = x
                elif (key == 'operation_mode'):
                    for x in value:
                        for i in value[x]:
                            for y in value[x][i]:
                                if (y == 'duration'):
                                    duration = int(value[x][i][y])
                                elif (y == 'start_date'):
                                    st_date = value[x][i][y]
        
        tmp = datetime.strptime(st_date, '%d-%m-%Y') + timedelta(days=duration)
        end_date = tmp.strftime('%d-%m-%Y')
        now = datetime.now().strftime('%d-%m-%Y')

        if (now == end_date):
            # It's time to be deleted
            # 1. Update operation mode to 'delete'
            PSM_OUTPUT = PSM_DIR + 'PSM-' + req_uuid + '.yaml'
            fin = open(PSM_OUTPUT, "rt")
            data = fin.read()
            data = data.replace('create', 'delete')
            data = data.replace('modify', 'delete')
            fin.close()
            fin = open(PSM_OUTPUT, "wt")
            fin.write(data)
            fin.close()
            
            # 2. Generate preempt file to be deleted
            pattern = 'preempt-'
            listFiles = [f for f in os.listdir(PREEMPT_PATH) if f.startswith(pattern)]
            priorities = []
            try:
                for p in listFiles:
                    with open(PREEMPT_PATH + p, 'r') as conversionfile:
                        for key, value in yaml.full_load(conversionfile).items():
                            [priorities.append(value[x]) for x in value if x == 'priority']                                    
                priority = max(priorities) + 1
            except:
                priority = 0
            
            preemptData = dict(
                preempt=dict(
                    uuid=req_uuid,
                    priority=priority,
                    destination=bestNode,
                    state='ready',
                    arrival_time=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    start_date=end_date
                )
            )
            with open(PREEMPT_PATH + 'preempt-' + req_uuid + '.yaml', 'w') as outfile:
                yaml.dump(preemptData, outfile, default_flow_style=False)

def main():
    """
    Responsible for verifying if there are services that exceed the maximum duration.
    Performs the creation or destruction of the service.
    Eventually is responsible for rearranging the preempts.
    """
    
    # 1. Creates preempt files for services that are about to end
    checkDuration()
    
    # 2. Adds to the Priority queue all preempts with a start date less than a day from current date.
    pattern = 'preempt-'
    listFiles = [f for f in os.listdir(PREEMPT_PATH) if f.startswith(pattern)]
    q = PriorityQueue()
    for p in listFiles:
        with open(PREEMPT_PATH + p, 'r') as conversionfile:
            for key, value in yaml.full_load(conversionfile).items():
                for x in value:
                    if (x == 'start_date'):
                        start = datetime.strptime(value[x], '%d-%m-%Y')
                        now = datetime.now()
                        diff = start - now
                    elif (x == 'priority'):
                        priority = value[x]
                    elif (x == 'uuid'):
                        UUID = value[x]
        try:
            if (diff.days < 1):
                q.put((priority, UUID))
        except:
            pass

    # 3. The main loop of the program in which for each service in the queue by priority, its creation or destruction is executed.
    while not q.empty():
        next_item = q.get()
        print(next_item)
        UUID = next_item[1]
        PSM_DATA = {}
        PRODUCTION_PSM = str(PSM_DIR) + 'PSM-' + UUID + '.yaml'
        with open(PRODUCTION_PSM, 'r') as PSMfile:
            for key, value in yaml.full_load(PSMfile).items():
                PSM_DATA.update({key: value})
                if (key == 'operation_mode'):
                    for x in value:
                        op_mode = x
                elif (key == 'service'):
                    for x in value:
                        PSM_NAME = x  # Name of the PSM choosen
                        for i in value[x]:
                            if (i != 'lessons_url'):
                                VIRT_TECH = i
                elif (key == 'server'):
                    for x in value:
                        DEST_NODE = value[x]['network']['ip']

        sys.path.append(PATH_CODE)
        # Importing PSM Python file as a module
        psm = importlib.import_module(PSM_NAME, package=None)
        
        LOG_NAME = PROJECT_PATH + '/logs/log_' + UUID + '.log'
        logger = logging.getLogger(__name__)
        f_handler = logging.FileHandler(LOG_NAME)
        f_handler.setLevel(logging.WARNING)
        f_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
        logger.addHandler(f_handler)

        if (op_mode != 'delete'):
            logger.warning('Executing PSM code module of ' + PSM_NAME)
            process1 = psm.code(UUID, PROJECT_PATH, PSM_NAME, VIRT_TECH, PSM_DATA)
            process1.main()
            logger.warning('Code modified and ready to be deployed')

            logger.warning('Deploying with specific virtualization technology')
            process2 = psm.deploy(UUID, PROJECT_PATH, DEST_NODE, PSM_DATA)
            process2.main()
            logger.warning('Finished deploying')

        else:
            logger.warning('Executing the service destruction')
            deleteps = psm.destroy(UUID, PROJECT_PATH, DEST_NODE, PSM_DATA)
            deleteps.main()
            logger.warning('Finished destroying')

        os.remove(PREEMPT_PATH + 'preempt-' + UUID + '.yaml')

    # 4. Eventually, there is the need to rearrange the priority of remaining preempt files.
    pattern = 'preempt-'
    listFiles = [f for f in os.listdir(PREEMPT_PATH) if f.startswith(pattern)]
    priorities = []
    data = {}
    for p in listFiles:
        with open(PREEMPT_PATH + p, 'r') as conversionfile:
            for key, value in yaml.full_load(conversionfile).items():
                for x in value:
                    if (x == 'priority'):
                        priority = value[x]
                        priorities.append(priority)
                    elif(x == 'uuid'):
                        uuid = value[x]
        data.update({priority: uuid})

    try:
        # Re-arrange current preempt files if there are gaps between priorities
        gaps = [ele for ele in range(max(priorities)+1) if ele not in priorities]

        if (gaps):
            priorities.sort()
            arranged = {}
            tmp = list(range(len(priorities)))
            for x in priorities:
                new = tmp[0]
                del tmp[0]
                arranged.update({new: data[x]})

            for x in arranged:
                arrangePreempt = PREEMPT_PATH + 'preempt-' + arranged[x] + '.yaml'
                for k in data:
                    if data[k] == arranged[x]:
                        fin = open(arrangePreempt, "rt")
                        d = fin.read()
                        d = d.replace('  priority: ' + str(k),
                                        '  priority: ' + str(x))
                        fin.close()
                        fin = open(arrangePreempt, "wt")
                        fin.write(d)
                        fin.close()
    except:
        pass

if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
