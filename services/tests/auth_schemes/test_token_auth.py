import pytest

from services.api_connector.auth_schemes.token_auth import TokenAuthScheme
from services.api_connector.auth_schemes.exceptions import TokenRefreshError


@pytest.fixture()
def token_schema():
    return TokenAuthScheme('header', 'token')


def test_get_auth_data(token_schema):
    expected_auth_data = {'header': 'token'}
    assert token_schema.get_auth_data() == expected_auth_data


def test_update_auth_data(token_schema):
    with pytest.raises(TokenRefreshError) as exc_info:
        token_schema.update_auth_data()

    assert str(exc_info.value) == 'Static token cannot be refreshed.'
