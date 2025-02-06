import pytest

from services.api_connector.auth_schemes.jwt_auth import JWTAuthScheme


@pytest.fixture()
def jwt_schema():
    return JWTAuthScheme('accessToken', 'refreshToken')


def test_jwt_auth_schema(jwt_schema):
    expected = {'Authorization': 'Bearer accessToken'}
    assert jwt_schema.get_auth_data() == expected
