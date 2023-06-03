import pytest
from unittest.mock import patch
from custom_secrets_manager.secrets_loader import load_secrets
from anyconfig.common.errors import UnknownFileTypeError


@pytest.fixture
def yaml_content():
    return """
    database:
      host: localhost
      port: 5432
      username: myuser
      password: mypassword
    """


@pytest.fixture
def json_content():
    return """
    {
        "api_key": "my_api_key",
        "secret_key": "my_secret_key"
    }
    """


@pytest.fixture
def ini_content():
    return """
    [section]
    option1 = value1
    option2 = value2
    """


@patch("custom_secrets_manager.secrets_loader.anyconfig.load")
def test_load_secrets_from_yaml(mock_load, yaml_content):
    mock_load.return_value = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "myuser",
            "password": "mypassword",
        }
    }

    secrets = load_secrets("secrets.yaml")

    assert secrets is not None
    assert isinstance(secrets, dict)
    assert "database" in secrets
    assert secrets["database"]["host"] == "localhost"
    assert secrets["database"]["port"] == 5432
    assert secrets["database"]["username"] == "myuser"
    assert secrets["database"]["password"] == "mypassword"


@patch("custom_secrets_manager.secrets_loader.anyconfig.load")
def test_load_secrets_from_json(mock_load, json_content):
    mock_load.return_value = {"api_key": "my_api_key", "secret_key": "my_secret_key"}

    secrets = load_secrets("secrets.json")

    assert secrets is not None
    assert isinstance(secrets, dict)
    assert "api_key" in secrets
    assert "secret_key" in secrets
    assert secrets["api_key"] == "my_api_key"
    assert secrets["secret_key"] == "my_secret_key"


@patch("custom_secrets_manager.secrets_loader.anyconfig.load")
def test_load_secrets_from_ini(mock_load, ini_content):
    mock_load.return_value = {"section": {"option1": "value1", "option2": "value2"}}

    secrets = load_secrets("secrets.ini")

    assert secrets is not None
    assert isinstance(secrets, dict)
    assert "section" in secrets
    assert "option1" in secrets["section"]
    assert "option2" in secrets["section"]
    assert secrets["section"]["option1"] == "value1"
    assert secrets["section"]["option2"] == "value2"


def test_load_secrets_from_unknown_file_type():
    with pytest.raises(FileNotFoundError):
        load_secrets("secrets.txt")
