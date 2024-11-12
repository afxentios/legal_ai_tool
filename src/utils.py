import logging
import yaml
import os


# Implement a logging configuration to monitor application behavior and facilitate debugging.

def load_config(config_path='config/config.yaml'):
    """
       Loads the configuration from config/config.yaml relative to the script's directory.

       Returns:
           dict: Configuration parameters.
       """
    try:
        # Determine the absolute path to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the absolute path to config.yaml
        config_path = os.path.join(script_dir, '..', 'config', 'config.yaml')

        # Open and load the YAML configuration file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise

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
