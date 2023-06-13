starter_process: A utility for managing secrets and API keys
---

This starter_process script performs the following tasks:
  - Creates a `secrets_registry.log` file as a database for secrets, API keys, or passwords found in the parent directory of the script.
  - Scans the parent directory for suggestive file names like secrets or keys with file extensions **`.yaml`**, **`.json`**, or **`.ini`**. If there is a mention of a key name without a value, it checks the corresponding value in `os.environ` and updates the registry accordingly.
  - Makes available a `secrets_loader.py` module to load secrets from the secrets_registry.log file.
  - Generates meaningful logs in the standard output and saves logs in the `load_config_process.log` file in the same directory.
  - Checks if a `.gitignore` file exists in the directory and ensures that entries are made for secrets files.

Please note that this script assumes that you have the secrets_loader.py module in the same directory as `starter_process.py`