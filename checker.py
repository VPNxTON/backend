from time import sleep

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger('checker')


def check(sub):
    pass


def worker():
    logger.info('Start service')
    while True:
        sleep(60)

if __name__ == '__main__':
    worker()