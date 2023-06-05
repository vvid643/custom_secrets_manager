import os
import ast
import json
import anyconfig
from anyconfig.common.errors import UnknownFileTypeError
from custom_secrets_manager.encryption_helper import decrypt_data


def parse_content(content):
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
    try:
        secrets = anyconfig.load(file_path)
    except UnknownFileTypeError:
        raise FileNotFoundError(f"No parser found for file: {file_path}")

    return secrets


def use_secrets(decryption_key, disable_encryption=False):
    parent_dir = os.getcwd()
    secrets_registry_file = os.path.join(parent_dir, "secrets_registry.log")

    if disable_encryption:
        with open(secrets_registry_file, "r") as f:
            decrypted_data = f.read()
    else:
        with open(secrets_registry_file, "r") as f:
            encrypted_data = f.read()

        decrypted_data = decrypt_data(encrypted_data, decryption_key)

    secrets_registry = {}
    for line in decrypted_data.splitlines():
        key, value = line.split(":", 1)  # Split on the first occurrence of ":"
        secrets_registry[key.strip()] = parse_content(value.strip())

    return secrets_registry
