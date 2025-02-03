from services.api_connector import RestClient


class Provider:

    URI_CONTRACT_EVENTS = '/v1/contracts/{address}/events'

    request_client: RestClient = None

    def __init__(self, base_url, auth_scheme):
        self.auth_scheme = auth_scheme
        if Provider.request_client is None:
            Provider.request_client = RestClient(base_url, auth_scheme)

    def get_contract_events(self, block_number: int, offset: int, contract_address: str):
        endpoint = self.URI_CONTRACT_EVENTS.format(address=contract_address)
        params = {
            'event_name': 'Transfer',
            'block_number': block_number,
            'limit': offset
        }

        while True:
            events_data = self.request_client.get(endpoint=endpoint, params=params).json()
            yield events_data
            if events_data['meta'].get('links'):
                params['fingerprint'] = events_data['meta']['fingerprint']
            else:
                break
