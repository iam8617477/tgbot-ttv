import requests


class RestClient:
    def __init__(self, base_url, auth_scheme):
        self.base_url = base_url
        self.auth_scheme = auth_scheme
        self.headers = self.auth_scheme.get_auth_data()

    def _send_request(self, method, endpoint, params=None, data=None, json=None, headers=None):
        url = self.base_url + endpoint

        if headers is not None:
            self.headers.update(headers)

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=self.headers
        )

        if response.status_code == 401:
            self.headers.update(self.auth_scheme.update_auth_data())
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=self.headers
            )

        if response.status_code >= 200 and response.status_code < 300:
            return response
        else:
            response.raise_for_status()

    def get(self, endpoint, params=None, headers=None):
        return self._send_request('GET', endpoint, params=params, headers=headers)

    def post(self, endpoint, data=None, json=None, headers=None):
        return self._send_request('POST', endpoint, data=data, json=json, headers=headers)

    def put(self, endpoint, data=None, json=None, headers=None):
        return self._send_request('PUT', endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint, params=None, headers=None):
        return self._send_request('DELETE', endpoint, params=params, headers=headers)
