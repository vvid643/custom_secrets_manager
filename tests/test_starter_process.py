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
    key_file = ""
    disable_encryption = True

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
            parent_dir,
            secrets_registry_file,
            secrets_files,
            logger,
            secrets_registry,
            key_file,
            disable_encryption,
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


# @pytest.mark.parametrize("mock_git_repository", argvalues=[True, False])
@patch("custom_secrets_manager.starter_process.scan_secrets_files")
@patch("custom_secrets_manager.starter_process.update_secrets_registry")
@patch(
    "custom_secrets_manager.starter_process.os.getcwd",
    return_value=os.path.dirname(__file__),
)
@patch(
    "custom_secrets_manager.temp_log_cleanup.check_git_repository",
    # return_value="mock_git_repository",
)
def test_main(
    mock_os_getcwd,
    mock_update_secrets_registry,
    mock_scan_secrets_files,
    mock_git_repository,
):
    mock_git_repository.side_effect = [True]
    starter_process.main()

    # Add assertions to verify the expected behavior
    mock_scan_secrets_files.call_count == 1
    mock_update_secrets_registry.call_count == 2

    mock_git_repository.side_effect = [False]
    starter_process.main()

    mock_scan_secrets_files.call_count == 2
    # mock_load_secrets.assert_called_once()
