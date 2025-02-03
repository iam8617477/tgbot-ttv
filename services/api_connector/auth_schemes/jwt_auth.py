from .base import AuthScheme


class JWTAuthScheme(AuthScheme):
    def __init__(self, access_token, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_auth_data(self):
        return {'Authorization': f'Bearer {self.access_token}'}
