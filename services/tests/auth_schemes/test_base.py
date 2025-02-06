import pytest

from services.api_connector.auth_schemes.base import AuthScheme


def test_auth_scheme():
    auth = AuthScheme()
    with pytest.raises(NotImplementedError):
        auth.get_auth_data()
    with pytest.raises(NotImplementedError):
        auth.update_auth_data()
