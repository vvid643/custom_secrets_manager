import os
import pytest
import logging
from custom_secrets_manager.starter_process import update_secrets_registry


@pytest.fixture(scope="module")
def test_environment(tmpdir_factory):
    # Create a temporary directory for the test environment
    temp_dir = tmpdir_factory.mktemp("test_env")

    # Set the current working directory to the temporary directory
    os.chdir(temp_dir)

    # Create dummy secrets files
    secrets_yaml = temp_dir.join("secrets.yaml")
    secrets_yaml.write(
        "database:\n  host: localhost\n  port: 5432\n  username: myuser\n  password: mypassword"
    )
    secrets_json = temp_dir.join("secrets.json")
    secrets_json.write(
        '{"database": {"host": "localhost", "port": 5432, "username": "myuser", "password": "mypassword"}}'
    )
    secrets_ini = temp_dir.join("secrets.ini")
    secrets_ini.write(
        "[database]\nhost = localhost\nport = 5432\nusername = myuser\npassword = mypassword"
    )

    # Run the test using the temporary directory as the parent directory
    yield temp_dir

    # Teardown: Remove the temporary directory and its contents
    temp_dir.remove()


def test_integration_update_secrets_registry(test_environment):
    parent_dir = test_environment
    secrets_registry_file = "secrets_registry.log"
    secrets_files = ["secrets.yaml", "secrets.json", "secrets.ini"]

    # breakpoint()

    # Create a mock logger
    logger = logging.getLogger()

    # Initialize the secrets registry
    secrets_registry = {}

    # Call the function to update the secrets registry
    update_secrets_registry(
        parent_dir,
        secrets_registry_file,
        secrets_files,
        logger,
        secrets_registry,
    )

    # Assert that the secrets registry file was created
    assert os.path.exists(os.path.join(parent_dir, secrets_registry_file))

    # Assert that the secrets registry file is not empty
    assert os.path.getsize(secrets_registry_file) > 0

    # Assert that the secrets registry contains the expected values
    expected_registry = {
        "database": {
            "host": "localhost",
            "port": "5432",
            "username": "myuser",
            "password": "mypassword",
        },
    }
    assert secrets_registry == expected_registry
