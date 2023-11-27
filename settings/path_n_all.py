import os
import yaml
from yaml.loader import SafeLoader


class PrepareSettings:
    def __init__(self):
        self.project_path = os.getcwd()
        self.config_path= os.path.join(self.project_path, 'configuration')


        with open(os.path.join(self.config_path, 'config.yaml')) as f:
            self.config = yaml.load(f, Loader=SafeLoader)
            
        self.repo_store= self.config['repo_store']
        self.repo_size_limit=self.config['repo_size_limit']