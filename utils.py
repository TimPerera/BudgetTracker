import yaml
import logging

LOGGER_LEVEL = 'DEBUG'

def update_cfg(cfg):
    with open('configs.yaml','w') as configs:
        return yaml.dump(cfg, configs)
    
def load_saved_data():
    with open('configs.yaml','r') as configs:
        cfg = yaml.safe_load(configs)
    return cfg

def setupLogger(level=logging.INFO):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d', 
                        datefmt = '%Y-%m-%d %H:%M:s',
                        level=level)
    logger = logging.getLogger('BudgetLogger')
    return logger
logger = setupLogger(logging.DEBUG)


if __name__ == '__main__':
    setupLogger(logging.DEBUG)
    logging.info('Logger initialized')