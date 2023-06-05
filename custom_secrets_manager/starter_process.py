import argparse
import os
import logging
from logging.handlers import RotatingFileHandler
from custom_secrets_manager.secrets_loader import load_secrets
from custom_secrets_manager.encryption_helper import (
    save_encryption_key,
    encrypt_secrets,
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Starter Process")
    parser.add_argument(
        "-k",
        "--key-file",
        default="encryption_key.txt",
        help="Path to the encryption key file (default: encryption_key.txt)",
    )
    parser.add_argument(
        "-d",
        "--disable-encryption",
        action="store_true",
        help="Disable encryption of secrets registry",
    )
    return parser.parse_args()


def get_os_environ(key):
    return os.environ.get(key)


def check_git_repository(dir_path):
    """
    Check if the given directory is a git repository.

    Args:
        dir_path (str): Path to the directory.

    Returns:
        bool: True if the directory is a git repository, False otherwise.
    """
    git_dir = os.path.join(dir_path, ".git")
    return os.path.isdir(git_dir)


def check_gitignore(dir_path, logger):
    """
    Check if the directory contains a .gitignore file.

    Args:
        dir_path (str): Path to the directory.
        logger (logging.Logger): Logger instance.

    Returns:
        bool: True if .gitignore file is found, False otherwise.
    """
    expected_git_ignore_path = os.path.join(dir_path, ".gitignore")
    if os.path.isfile(expected_git_ignore_path):
        logger.info("Found .gitignore...")
        return True
    else:
        logger.info(".gitignore not found, creating one...")
        return False


def update_gitignore(dir_path, logger):
    """
    Update the .gitignore file to include "secrets_registry.log" and "load_config_process.log".

    Args:
        dir_path (str): Path to the directory.
        logger (logging.Logger): Logger instance.

    If the .gitignore file does not exist, it will be created.
    """
    gitignore_path = os.path.join(dir_path, ".gitignore")
    secrets_registry_entry = "secrets_registry.log"
    load_config_entry = "load_config_process.log"

    with open(gitignore_path, "a+") as f:
        f.seek(0)
        content = f.read()
        if secrets_registry_entry not in content:
            f.write(f"\n{secrets_registry_entry}\n")
        if load_config_entry not in content:
            f.write(f"{load_config_entry}\n")

    logger.info(".gitignore file updated")


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
    parent_dir,
    secrets_registry_file,
    secrets_files,
    logger,
    secrets_registry,
    key_file,
    disable_encryption,
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

    if not disable_encryption:
        encrypted_secrets = encrypt_secrets(secrets_registry, key_file)
        # Write the encrypted secrets to the secrets_registry.log file
        with open(os.path.join(parent_dir, secrets_registry_file), "wb") as f:
            f.write(encrypted_secrets)
        logger.info("Secrets registry encrypted and written to secrets_registry.log")
    else:
        logger.warning(
            "Secrets will be stored without encryption. This is NOT recommended. "
            "Please delete the secrets_registry.log after reading to avoid a security lapse."
        )
        with open(os.path.join(parent_dir, secrets_registry_file), "w") as f:
            for key, value in secrets_registry.items():
                f.write(f"{key}: {value}\n")


def main():
    """
    Main entry point of the starter process.
    """
    # Parse command line arguments
    args = parse_arguments()
    key_file = args.key_file
    disable_encryption = args.disable_encryption

    # Configuration
    current_dir = os.getcwd()
    secrets_registry_file = os.path.join(current_dir, "secrets_registry.log")
    log_file = "load_config_process.log"

    # Set up logging
    logger = setup_logging(log_file)

    # Save encryption key
    if not disable_encryption:
        if key_file == "encryption_key.txt":
            key_file = os.path.join(current_dir, key_file)

        save_encryption_key(key_file, logger)

    # Scan parent directory for secrets files
    secrets_files = scan_secrets_files(current_dir)

    # Initialize secrets registry
    secrets_registry = {}

    # Update secrets registry
    update_secrets_registry(
        current_dir,
        secrets_registry_file,
        secrets_files,
        logger,
        secrets_registry,
        key_file,
        disable_encryption,
    )

    # Check if the current directory is a git repository
    if check_git_repository(current_dir):
        check_gitignore(current_dir, logger)
        update_gitignore(current_dir, logger)


if __name__ == "__main__":
    main()
