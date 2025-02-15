import os
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, wait, ALL_COMPLETED

import django
from django.db import transaction
from tronpy import Tron

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from services.api_connector import TokenAuthScheme
from indexer.models import Block, Contract, Event, Wallet
from indexer.chain import Provider


logging.basicConfig(level=logging.INFO)
tron = Tron()

API_BASE_URL = os.environ.get('CHAIN_API')
API_KEY_HEADER = os.environ.get('CHAIN_API_KEY_HEADER')
API_TOKEN = os.environ.get('CHAIN_API_TOKEN')
CONTRACT_ADDRESS = os.environ.get('CHAIN_CONTRACT_ADDRESS')
CONFIRMATIONS_COUNT = 0
PAUSE_SECONDS = (0.5, 10)
MAX_WORKERS = 5
TIMEOUT = 15
TIMEOUT_SEMAPHORE = 0.001


class SemaphoreWithDelay:
    def __init__(self, semaphore: threading.Semaphore, min_duration: float):
        self.semaphore = semaphore
        self.min_duration = min_duration
        self.thread_data = threading.local()

    def __enter__(self):
        self.semaphore.acquire()
        self.thread_data.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = time.time() - self.thread_data.start_time
        remaining_time = self.min_duration - elapsed_time

        if remaining_time > 0:
            logging.warning(f'Sleeping SemaphoreWithDelay for {remaining_time:.2f} sec...')
            time.sleep(remaining_time)

        self.semaphore.release()


class Processing:
    block_model = Block
    contract_model = Contract
    event_model = Event
    wallet_model = Wallet

    def __init__(self, provider: Provider):
        self.chain_provider = provider
        self.event = threading.Event()
        self.event.set()

    def get_last_block(self):
        return self.chain_provider.get_latest_block()

    def get_unprocessed_blocks(self, contract_address, size=100):
        unprocessed_blocks_qs = self.block_model.objects.filter(
            contract__address=contract_address,
            processed=False,
        ).order_by('-number')
        if unprocessed_blocks_qs.exists():
            return unprocessed_blocks_qs[:size]

    def get_contract_processing_time(self, address):
        if self.block_model.objects.filter(contract__address=address, processed=False).exists():
            return PAUSE_SECONDS[0]
        return PAUSE_SECONDS[1]

    def create_blocks(self, contract, start_number, end_number):
        for block_number in range(start_number, end_number+1):
            block = self.block_model.objects.create(
                contract=contract,
                number=block_number,
            )
            logging.info(f'{block} was created')

    def save_block_events(self, contract, block):
        for event_data in self.chain_provider.get_contract_events(
                contract_address=contract.address, block_number=block.number
        ):
            if wallet_address := self.wallet_model.objects.filter(
                    address=tron.to_base58check_address(event_data['result']['to'])
            ).first():
                event, created = self.event_model.objects.get_or_create(
                    transaction_id=event_data['transaction_id'],
                    defaults={
                        'value': event_data['result']['value'],
                        'to_address': wallet_address,
                        'unconfirmed': event_data.get('_unconfirmed', False),
                        'contract_address': contract,
                        'block': block,
                    }
                )

    def events_processing(self, contract, unprocessed_block):
        try:
            with transaction.atomic():
                self.save_block_events(contract, unprocessed_block)
                unprocessed_block.processed = True
                unprocessed_block.save()
                return f'{unprocessed_block} was processed'
        except Exception as e:
            unprocessed_block.error_message = str(e)[:255]
            unprocessed_block.save()
            raise e

    def stop(self):
        self.event.clear()

    def contract_processing(self, contract):
        unprocessed_blocks = self.get_unprocessed_blocks(contract.address)
        if unprocessed_blocks is None:
            return

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = list()
            for block in unprocessed_blocks:
                futures.append(executor.submit(self.events_processing, contract, block))
            try:
                for future in as_completed(futures, timeout=TIMEOUT):
                    if raise_exception := future.exception():
                        logging.error(f'contract_processing {contract.address}: {raise_exception}')
                    else:
                        logging.info(future.result())
            except TimeoutError:
                logging.warning(f'Tasks for {contract.address} were not completed on time.')

            for future in futures:
                if not future.done():
                    future.cancel()

            wait(futures, return_when=ALL_COMPLETED)

    def contract_cycle(self, contract):
        while self.event.is_set():
            logging.info(f'Processing contract: {contract.address}')
            last_block_chain = self.get_last_block() - CONFIRMATIONS_COUNT
            last_block_db = self.block_model.objects.filter(contract=contract).order_by('-number').first().number
            self.create_blocks(contract=contract, start_number=last_block_db+1, end_number=last_block_chain)
            self.contract_processing(contract)
            seconds = self.get_contract_processing_time(contract.address)
            logging.info(f'Pause for contract: {contract.address} is {seconds} seconds...')
            time.sleep(seconds)

    def run(self):
        logging.info(f'Run indexer')
        contracts = self.contract_model.objects.filter(blocks__isnull=False).distinct()
        logging.info(f'Number of contracts for indexing {contracts.count()}')
        thread_contracts = list()
        for contract in contracts:
            logging.info(f'Run contract cycle for: {contract.address}')
            thread = threading.Thread(target=self.contract_cycle, args=(contract, ))
            thread_contracts.append(thread)
            thread.start()
        try:
            for thread in thread_contracts:
                thread.join()
        except KeyboardInterrupt:
            logging.warning('KeyboardInterrupt detected! Stopping all threads...')
            self.stop()


def main():
    processing = Processing(
        provider=Provider(
            base_url=API_BASE_URL,
            auth_scheme=TokenAuthScheme(header=API_KEY_HEADER, token=API_TOKEN),
            semaphore=SemaphoreWithDelay(threading.Semaphore(), TIMEOUT_SEMAPHORE)
        )
    )

    processing.run()


if __name__ == '__main__':
    main()
