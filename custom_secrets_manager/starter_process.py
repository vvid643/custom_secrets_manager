import os

from custom_secrets_manager.secrets_loader import load_secrets
from custom_secrets_manager.encryption_helper import (
    save_encryption_key,
    encrypt_secrets,
)
from custom_secrets_manager.workflow_helper import setup_starter, sanitise_secrets_logs
from custom_secrets_manager.constants import _PLAUSIBLE_FILE_EXT, _PLAUSIBLE_KEY_NAMES


def get_os_environ(key):
    return os.environ.get(key)


def scan_secrets_files(parent_dir, scan_file_ext=None):
    """
    Scan the parent directory for secrets files.

    Args:
        parent_dir (str): Path to the parent directory.
        scan_file_ext (list): File types where secrets are to be scanned

    Returns:
        list: List of secrets file paths.
    """
    if scan_file_ext is None:
        scan_file_ext = _PLAUSIBLE_FILE_EXT
    secrets_files = []
    for f in os.listdir(parent_dir):
        if any(keyword in f.lower() for keyword in _PLAUSIBLE_KEY_NAMES) and any(
            f.endswith(extension) for extension in scan_file_ext
        ):
            secrets_files.append(f)
    return secrets_files


def update_secrets_registry(
    parent_dir,
    secrets_registry_file,
    secrets_files,
    logger,
    secrets_registry,
    key_file=None,
    disable_encryption=False,
):
    """
    Update the secrets registry with secrets from files.

    Args:
        parent_dir (str): Path to the parent directory.
        secrets_registry_file (str): Path to the secrets registry file.
        secrets_files (list): List of secrets file paths.
        logger (logging.Logger): Logger instance.
        secrets_registry (dict): Dictionary to store the secrets registry.
        key_file (str): Path where encryption key is stored. (Default None)
        disable_encryption (bool): If encryption is to be used. (Default False)
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
    # Load arguments, set up logger and log files
    args, logger, current_dir, secrets_registry_file = setup_starter()
    key_file = args.key_file
    disable_encryption = args.disable_encryption
    target_file_type = args.file_type

    # Save encryption key
    if not disable_encryption:
        if key_file == "encryption_key.txt":
            key_file = os.path.join(current_dir, key_file)

        save_encryption_key(key_file, logger)

    # Scan parent directory for secrets files
    if isinstance(target_file_type, str):
        target_file_type = [target_file_type]
    secrets_files = scan_secrets_files(current_dir, scan_file_ext=target_file_type)

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

    # Clean up files from git tracking
    sanitise_secrets_logs(current_dir, logger)


if __name__ == "__main__":
    main()
