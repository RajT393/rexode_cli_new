import logging

logging.basicConfig(filename='rexode_cli.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_action(action):
    logging.info(action)
