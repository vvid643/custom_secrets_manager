import anyconfig
from anyconfig.common.errors import UnknownFileTypeError


# Main function to load secrets from supported file types
def load_secrets(file_path):
    try:
        secrets = anyconfig.load(file_path)
    except UnknownFileTypeError:
        raise FileNotFoundError(f"No parser found for file: {file_path}")

    return secrets


# Example usage
# secrets_file = "secrets.yaml"
# secrets = load_secrets(secrets_file)

# Accessing secrets
# database_host = secrets["database"]["host"]
# database_username = secrets["database"]["username"]
# database_password = secrets["database"]["password"]
# api_key = secrets["api_key"]
