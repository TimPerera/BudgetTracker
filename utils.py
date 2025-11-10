import yaml

def update_cfg(cfg):
    with open('configs.yaml','w') as configs:
        return yaml.dump(cfg, configs)
    
def load_saved_data():
    with open('configs.yaml','r') as configs:
        cfg = yaml.safe_load(configs)
    return cfg
