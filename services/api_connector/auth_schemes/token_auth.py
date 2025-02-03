from .base import AuthScheme
from .exceptions import TokenRefreshError


class TokenAuthScheme(AuthScheme):
    def __init__(self, header, token):
        self.header = header
        self.token = token

    def get_auth_data(self):
        return {self.header: self.token}

    def update_auth_data(self):
        raise TokenRefreshError('Static token cannot be refreshed.')
