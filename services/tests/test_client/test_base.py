import pytest
from unittest.mock import Mock, patch

from services.api_connector import RestClient, TokenAuthScheme
from services.api_connector.auth_schemes.exceptions import TokenRefreshError


@pytest.fixture(scope='class')
def rest_client():
    return RestClient('base_url', TokenAuthScheme('header', 'token'))


@pytest.fixture
def mock_request(request):
    status_code = request.param
    with patch('requests.request') as mock_request:
        mock_response = Mock(status_code=status_code)
        if status_code not in [200, 401]:
            mock_response.raise_for_status.side_effect = Exception()
        mock_request.return_value = mock_response
        yield mock_request


@pytest.mark.parametrize('mock_request', [200], indirect=True)
class TestBaseMethods:
    class TestGet:
        def test_get(self, rest_client, mock_request):
            response = rest_client.get(endpoint='endpoint')
            assert response.status_code == 200

    class TestPost:
        def test_post(self, rest_client, mock_request):
            response = rest_client.post(endpoint='endpoint')
            assert response.status_code == 200

    class TestPut:
        def test_put(self, rest_client, mock_request):
            response = rest_client.put(endpoint='endpoint')
            assert response.status_code == 200

    class TestDelete:
        def test_delete(self, rest_client, mock_request):
            response = rest_client.delete(endpoint='endpoint')
            assert response.status_code == 200


class TestStatusCode:
    @pytest.mark.parametrize('mock_request', [401], indirect=True)
    def test_status_code_401(self, rest_client, mock_request):
        with pytest.raises(TokenRefreshError) as exc_info:
            rest_client.delete(endpoint='endpoint')

        assert str(exc_info.value) == 'Static token cannot be refreshed.'

    @pytest.mark.parametrize('mock_request', [300, 404], indirect=True)
    def test_status_code_not_200(self, rest_client, mock_request):
        with pytest.raises(Exception):
            rest_client.delete(endpoint='endpoint')
