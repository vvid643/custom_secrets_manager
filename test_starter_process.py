import os
import logging
import pytest
from unittest.mock import patch, Mock
from custom_secrets_manager import starter_process

from custom_secrets_manager.starter_process import (
    update_secrets_registry,
)


@pytest.fixture
def mock_load_secrets(mocker):
    # Mock the load_secrets function
    return mocker.patch("custom_secrets_manager.starter_process.load_secrets")


@pytest.fixture
def mock_open(mocker):
    # Mock the open function
    return mocker.mock_open()


def test_update_secrets_registry(mock_open, mock_load_secrets):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_registry_file = "secrets_registry.log"
    secrets_files = ["secrets.yaml"]

    # Mock the return value of load_secrets
    mock_load_secrets.return_value = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "myuser",
            "password": "mypassword",
        },
        "MY_KEY": None,
    }

    # Mock the os.environ dictionary
    mock_environ = {
        "MY_KEY": "env_value",
        "OTHER_KEY": "other_value",
    }

    with patch.dict("os.environ", mock_environ):
        # Create a mock logger
        logger = logging.getLogger()

        # Initialize the secrets registry
        secrets_registry = {}

        # Call the function to update the secrets registry
        update_secrets_registry(
            parent_dir, secrets_registry_file, secrets_files, logger, secrets_registry
        )

        # Assert that load_secrets was called with the correct file path
        file_path = os.path.join(parent_dir, secrets_files[0])
        mock_load_secrets.assert_called_once_with(file_path)

        # Assert that secrets_registry contains the expected values
        expected_registry = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "username": "myuser",
                "password": "mypassword",
            },
            "MY_KEY": "env_value",
        }
        assert secrets_registry == expected_registry

        # Assert that open was not called
        mock_open.assert_not_called()


@patch("custom_secrets_manager.starter_process.setup_logging")
@patch("custom_secrets_manager.starter_process.scan_secrets_files")
@patch("custom_secrets_manager.starter_process.update_secrets_registry")
def test_main(
    mock_update_secrets_registry,
    mock_scan_secrets_files,
    mock_setup_logging,
):
    starter_process.main()

    # Add assertions to verify the expected behavior
    mock_setup_logging.assert_called_once()
    mock_scan_secrets_files.assert_called_once()
    mock_update_secrets_registry.assert_called_once()
    # mock_load_secrets.assert_called_once()
