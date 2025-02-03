import os
import pprint
import sys

import django
import time

from services.api_connector import TokenAuthScheme
from indexer.chain import Provider

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

API_BASE_URL = os.environ.get('CHAIN_API')
API_KEY_HEADER = os.environ.get('CHAIN_API_KEY_HEADER')
API_TOKEN = os.environ.get('CHAIN_API_TOKEN')
CONTRACT_ADDRESS = os.environ.get('CHAIN_CONTRACT_ADDRESS')


last_block = 69321945
chain_provider = Provider(
    base_url=API_BASE_URL,
    auth_scheme=TokenAuthScheme(header=API_KEY_HEADER, token=API_TOKEN),
)
while True:
    try:
        for event in chain_provider.get_contract_events(
            block_number=last_block,
            offset=40,
            contract_address=CONTRACT_ADDRESS
        ):
            print(last_block, len(event['data']))
        # break
    except Exception as e:
        print("error:", e)
        break
    time.sleep(3)
    last_block += 1
