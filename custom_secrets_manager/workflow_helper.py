import argparse
import logging
from logging.handlers import RotatingFileHandler
import os

from custom_secrets_manager.temp_log_cleanup import run_git_cleanup
from custom_secrets_manager.constants import logger_filename, secrets_registry_filename


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.

    Raises:
        ValueError: If an invalid file type or directory path is provided.
    """
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
    parser.add_argument(
        "-t",
        "--file-type",
        default=None,
        type=str,
        required=False,
        help="Secrets file extension",
    )
    parser.add_argument(
        "-dir",
        default=None,
        required=False,
        help="Directory where secrets files are to be scanned",
    )

    args = parser.parse_args()

    if args.file_type and not args.file_type.startswith("."):
        raise ValueError("Invalid file type. File type should start with a dot (.)")

    if args.dir and not os.path.isdir(args.dir):
        raise ValueError("Invalid directory path.")

    return args


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


def sanitise_secrets_logs(current_dir, logger):
    """
    Perform sanitization of secrets logs.

    Args:
        current_dir (str): Current directory.
        logger (logging.Logger): Logger instance.
    """
    run_git_cleanup(current_dir=current_dir, logger=logger)


def setup_starter():
    """
    Set up the starter process.

    Returns:
        tuple: Parsed command line arguments (args) and logger instance (logger).
    """
    # Parse command line arguments
    args = parse_arguments()
    target_dir = args.dir

    # Configuration
    current_dir = os.getcwd() if target_dir is None else target_dir
    secrets_registry_file = os.path.join(current_dir, secrets_registry_filename)
    log_file = logger_filename

    # Set up logging
    logger = setup_logging(log_file)
    return args, logger, current_dir, secrets_registry_file
