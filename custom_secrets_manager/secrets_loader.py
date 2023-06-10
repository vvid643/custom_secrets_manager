import os
import ast
import json
import anyconfig
from anyconfig.common.errors import UnknownFileTypeError
from custom_secrets_manager.encryption_helper import decrypt_data


def parse_content(content):
    """
    Parse the content as a dictionary if possible, otherwise return it as is.

    Args:
        content (str): Content to be parsed.

    Returns:
        dict or str: Parsed content if it can be parsed as a dictionary, otherwise the content as is.
    """
    try:
        # Try to evaluate the content as a literal dictionary
        parsed_content = ast.literal_eval(content)
        if isinstance(parsed_content, dict):
            return _parse_nested_dict(parsed_content)
    except (ValueError, SyntaxError):
        pass

    try:
        # Try to load the content as JSON
        parsed_content = json.loads(content)
        if isinstance(parsed_content, dict):
            return _parse_nested_dict(parsed_content)
    except json.JSONDecodeError:
        pass

    # Return the content as is if it cannot be parsed as a dictionary
    return content


def _parse_nested_dict(dictionary):
    """
    Recursively parse a nested dictionary.

    Args:
        dictionary (dict): Nested dictionary to be parsed.

    Returns:
        dict: Parsed nested dictionary.
    """
    parsed_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, str):
            parsed_dict[key] = parse_content(value)
        elif isinstance(value, dict):
            parsed_dict[key] = _parse_nested_dict(value)
        else:
            parsed_dict[key] = value
    return parsed_dict


# Main function to load secrets from supported file types
def load_secrets(file_path):
    """
    Load secrets from a file.

    Args:
        file_path (str): Path to the secrets file.

    Returns:
        dict: Loaded secrets.

    Raises:
        UnknownFileTypeError: If the file cant be parsed by anyconfig.
        IOError: If there is an error reading the file.
    """
    try:
        secrets = anyconfig.load(file_path)
    except UnknownFileTypeError:
        raise FileNotFoundError(f"No parser found for file: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading secrets file: {str(e)}")

    return secrets


def use_secrets(decryption_key, disable_encryption=False):
    """
    Load and parse the secrets registry file.

    Args:
        decryption_key (str): Decryption key to decrypt the secrets registry file.
        disable_encryption (bool): Flag indicating whether encryption is disabled (default: False).

    Returns:
        dict: Secrets registry containing parsed secrets.

    Raises:
        FileNotFoundError: If the secrets registry file is not found.
        PermissionError: If there is a permission error while reading the secrets registry file.
        ValueError: If the secrets registry file cannot be decrypted.
    """
    parent_dir = os.getcwd()
    secrets_registry_file = os.path.join(parent_dir, "secrets_registry.log")

    try:
        with open(secrets_registry_file, "r") as f:
            if disable_encryption:
                decrypted_data = f.read()
            else:
                encrypted_data = f.read()
                decrypted_data = decrypt_data(encrypted_data, decryption_key)
    except FileNotFoundError:
        raise FileNotFoundError(
            "Secrets registry file not found: {}".format(secrets_registry_file)
        )
    except PermissionError:
        raise PermissionError(
            "Permission denied while reading secrets registry file: {}".format(
                secrets_registry_file
            )
        )
    except ValueError:
        raise ValueError(
            "Failed to decrypt secrets registry file with the provided decryption key"
        )

    secrets_registry = {}
    for line in decrypted_data.splitlines():
        key, value = line.split(":", 1)  # Split on the first occurrence of ":"
        secrets_registry[key.strip()] = parse_content(value.strip())

    return secrets_registry
