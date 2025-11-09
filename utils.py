def clean_desc(desc):
    desc = desc.strip()
    if '[IN]' in desc:
        return 'Interest Charge'
    if len(desc)==4:
        return desc
    else:
        return desc[4:]
    

def load_saved_data():
    with open('configs.yaml','r') as configs:
        cfg = yaml.safe_load(configs)
    return cfg