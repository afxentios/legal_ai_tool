import yaml
from typing import Any, Dict


class ConfigLoader:
    """
    Class to load and store configuration data.
    """

    @staticmethod
    def load_config(file_path: str) -> Dict[str, Any]:
        """
        Loads YAML configuration from the specified path.

        Args:
            file_path (str): Path to the YAML configuration file.

        Returns:
            Dict[str, Any]: Configuration data as a dictionary.
        """
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
