import yaml
from pathlib import Path 

def load_config_file(config_file):
    with open(config_file,"r") as file :
        config = yaml.safe_load(file)
    return config 