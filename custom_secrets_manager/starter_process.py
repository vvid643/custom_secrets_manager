import os
import logging
from logging.handlers import RotatingFileHandler
from custom_secrets_manager.secrets_loader import load_secrets


def get_os_environ(key):
    return os.environ.get(key)


def setup_logging(log_file):
    """
    Set up logging configuration.

    Args:
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_formatter = logging.Formatter(log_format)
    log_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=3)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger


def scan_secrets_files(parent_dir):
    """
    Scan the parent directory for secrets files.

    Args:
        parent_dir (str): Path to the parent directory.

    Returns:
        list: List of secrets file paths.
    """
    secrets_files = []
    for f in os.listdir(parent_dir):
        if any(keyword in f.lower() for keyword in ["secrets", "keys"]) and any(
            f.endswith(extension) for extension in [".yaml", ".json", ".ini"]
        ):
            secrets_files.append(f)
    return secrets_files


def update_secrets_registry(
    parent_dir, secrets_registry_file, secrets_files, logger, secrets_registry
):
    """
    Update the secrets registry with secrets from files.

    Args:
        parent_dir (str): Path to the parent directory.
        secrets_registry_file (str): Path to the secrets registry file.
        secrets_files (list): List of secrets file paths.
        logger (logging.Logger): Logger instance.
        secrets_registry (dict): Dictionary to store the secrets registry.
    """
    for secrets_file in secrets_files:
        file_path = os.path.join(parent_dir, secrets_file)
        secrets = load_secrets(file_path)
        for key, value in secrets.items():
            if value is None:
                env_value = get_os_environ(key)
                if env_value:
                    secrets_registry[key] = env_value
                    logger.info(f"Added secret '{key}' from environment variables")
                else:
                    secrets_registry.pop(key, None)
                    logger.info(f"Dropped secret '{key}' from registry")
            else:
                secrets_registry[key] = value
                logger.info(f"Added secret '{key}' from '{secrets_file}'")

    with open(os.path.join(parent_dir, secrets_registry_file), "w") as f:
        for key, value in secrets_registry.items():
            f.write(f"{key}: {value}\n")


def main():
    """
    Main entry point of the starter process.
    """
    # Configuration
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_registry_file = "secrets_registry.log"
    log_file = "load_config_process.log"

    # Set up logging
    logger = setup_logging(log_file)

    # Scan parent directory for secrets files
    secrets_files = scan_secrets_files(parent_dir)

    # Update secrets registry
    update_secrets_registry(parent_dir, secrets_registry_file, secrets_files, logger)

    # Example usage
    # database_host = secrets['database']['host']
    # database_username = secrets['database']['username']
    # database_password = secrets['database']['password']
    # api_key = secrets['api_key']


if __name__ == "__main__":
    main()
