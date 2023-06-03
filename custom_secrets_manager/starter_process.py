import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import anyconfig
import secrets_loader


def main():
    # Configure logging
    log_file = "load_config_process.log"
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_formatter = logging.Formatter(log_format)
    log_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=3)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    # Create a secrets registry file
    secrets_registry_file = "secrets_registry.log"

    # Scan the parent directory for secrets files
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_files = []
    for f in os.listdir(parent_dir):
        if any(keyword in f.lower() for keyword in ["secrets", "keys"]) and any(
            f.endswith(extension) for extension in [".yaml", ".json", ".ini"]
        ):
            secrets_files.append(f)

    # Load secrets from identified files and update the registry
    secrets_registry = {}
    for secrets_file in secrets_files:
        file_path = os.path.join(parent_dir, secrets_file)
        secrets = anyconfig.load(file_path)
        for key, value in secrets.items():
            if value is None:
                env_value = os.environ.get(key)
                if env_value:
                    secrets_registry[key] = env_value
                    logger.info(f"Added secret '{key}' from environment variables")
                else:
                    secrets_registry.pop(key, None)
                    logger.info(f"Dropped secret '{key}' from registry")
            else:
                secrets_registry[key] = value
                logger.info(f"Added secret '{key}' from '{secrets_file}'")

    # Write the secrets registry to the file
    with open(secrets_registry_file, "w") as f:
        for key, value in secrets_registry.items():
            f.write(f"{key}: {value}\n")

    # Use secrets_loader module to load secrets from the registry
    secrets = secrets_loader.load_secrets(secrets_registry_file)

    # Example usage
    # database_host = secrets['database']['host']
    # database_username = secrets['database']['username']
    # database_password = secrets['database']['password']
    # api_key = secrets['api_key']


if __name__ == "__main__":
    main()
