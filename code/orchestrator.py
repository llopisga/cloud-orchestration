#!/usr/bin/python3
# coding=utf-8
"""
Description:
    - Model Orchestrator
"""
__author__ = "Raúl Llopis Gandia"
__version__ = "1"
__email__ = "raullg8@gmail.com"
__status__ = "Final Project"

import os
import sys
import time
import yaml
import signal
import logging
import logging.handlers
from psm import policies
from pim import conversionPIM
from emailClient import errorEmail
from feasibles import feasiblesPSM

start_time = time.time()

# Kill parent process 'bash_call.sh' and continue execution
os.kill(os.getppid(), signal.SIGTERM)

with open("./conf/config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Global variables
UUID = sys.argv[1]
TM_PATH = config['TM_PATH']
PROJECT_PATH = config['PROJECT_PATH'].replace("USERNAME", os.getenv('USER'))

SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = config['SMTP_PORT']
FROM = config['NOTIFY_ADMIN']
TO = config['NOTIFY_ADMIN']
MSG = 'Error handled for service ' + UUID + ' in Model Orchestrator!'
AUTH_USER = os.environ['MAIL_USERNAME']
AUTH_TOKEN = os.environ['MAIL_TOKEN']

logger = logging.getLogger()
se = errorEmail((SMTP_SERVER, SMTP_PORT), FROM,
                TO, MSG, (AUTH_USER, AUTH_TOKEN))
se.setLevel(logging.ERROR)
logger.addHandler(se)


def main():
    try:
        process1 = conversionPIM(UUID, TM_PATH, PROJECT_PATH)
        process1.main()

        process2 = feasiblesPSM(UUID, PROJECT_PATH)
        process2.main()

        process3 = policies(UUID, PROJECT_PATH)
        process3.main()

    except Exception:
        logger.exception('Unhandled Exception')


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
