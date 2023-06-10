import os


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


def run_git_cleanup(current_dir, logger):
    """
    Check if the current directory is a git repository, check gitignore file,
    and update it if necessary.

    Args:
        current_dir (str): Current directory path.
        logger (logging.Logger): Logger instance.

    Returns:
        bool: True if git operations were successful, False otherwise.
    """
    if not check_git_repository(current_dir):
        logger.warning("Not a git repository. Skipping git clean up.")
        return False

    check_gitignore(current_dir, logger)

    update_gitignore(current_dir, logger)

    return True
