from cryptography.fernet import Fernet


# Generate encryption key
def generate_key():
    return Fernet.generate_key()


# Encrypt data using the encryption key
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)


# Decrypt data using the encryption key
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()


def encrypt_secrets(secrets_registry, key_file):
    """
    Encrypt the secrets registry and write it to the secrets_registry.log file.

    Args:
        secrets_registry (dict): Dictionary containing the secrets registry.
        key_file (str): Path to the encryption key file.
    """
    # Load the encryption key
    with open(key_file, "rb") as f:
        encryption_key = f.read()

    # Convert secrets registry to bytes
    secrets_data = "\n".join(
        f"{key}: {value}" for key, value in secrets_registry.items()
    )
    secrets_bytes = secrets_data.encode()

    # Encrypt the secrets
    encrypted_data = encrypt_data(secrets_bytes, encryption_key)

    return encrypted_data


def save_encryption_key(key_file_path, logger):
    logger.info("Generating encryption key...")
    key = generate_key()
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)
        print("Encryption key generated and saved to 'encryption_key.txt'")
