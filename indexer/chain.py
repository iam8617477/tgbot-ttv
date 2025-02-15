import time

from services.api_connector import RestClient


class Provider:

    URI_CONTRACT_EVENTS = '/v1/contracts/{address}/events'
    URI_TX_BY_ID_EVENTS = '/v1/transactions/{tx_id}/events'
    URI_LATEST_BLOCK = '/wallet/getblockbylatestnum'
    URI_BLOCK_NUM = '/wallet/getblockbynum'
    URI_GET_TX_BY_ID = '/wallet/gettransactionbyid'

    request_client: RestClient = None

    def __init__(self, base_url, auth_scheme, semaphore):
        self.auth_scheme = auth_scheme
        if Provider.request_client is None:
            Provider.request_client = RestClient(base_url, auth_scheme)
        self.semaphore = semaphore

    def get_contract_events(
            self,
            contract_address: str,
            block_number: int = None,
            min_block_timestamp: int = None,
            max_block_timestamp: int = None,
            offset: int = 200,
            event_name: str = 'Transfer'
    ):
        endpoint = self.URI_CONTRACT_EVENTS.format(address=contract_address)
        params = {
            'event_name': event_name,
            'limit': offset
        }
        if block_number:
            params['block_number'] = block_number
        if min_block_timestamp:
            params['min_block_timestamp'] = min_block_timestamp
        if max_block_timestamp:
            params['max_block_timestamp'] = max_block_timestamp

        while True:
            with self.semaphore:
                events_data = self.request_client.get(endpoint=endpoint, params=params).json()
            for event_data in events_data['data']:
                yield event_data
            if events_data['meta'].get('links'):
                params['fingerprint'] = events_data['meta']['fingerprint']
            else:
                break

    def get_tx_events(self, tx_id):
        endpoint = self.URI_TX_BY_ID_EVENTS.format(tx_id=tx_id)
        with self.semaphore:
            tx_events_data = self.request_client.get(endpoint=endpoint).json()
        return tx_events_data

    def get_latest_block(self):
        endpoint = self.URI_LATEST_BLOCK
        payload = {'num': 1}
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        with self.semaphore:
            last_block_data = self.request_client.post(endpoint=endpoint, json=payload, headers=headers).json()
        return last_block_data['block'][0]['block_header']['raw_data']['number'] - 1

    def get_block_num(self, num):
        endpoint = self.URI_BLOCK_NUM
        payload = {'num': num}
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        with self.semaphore:
            block_data = self.request_client.post(endpoint=endpoint, json=payload, headers=headers).json()
        return block_data

    def get_transaction_by_id(self, tx_id):
        endpoint = self.URI_GET_TX_BY_ID
        payload = {'value': tx_id, 'visible': True}
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        with self.semaphore:
            transaction_data = self.request_client.post(endpoint=endpoint, json=payload, headers=headers).json()
        return transaction_data
