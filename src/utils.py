import logging
import yaml
import os


# Implement a logging configuration to monitor application behavior and facilitate debugging.

def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def setup_logging(config):
    log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
    log_file = config['logging']['file']
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
