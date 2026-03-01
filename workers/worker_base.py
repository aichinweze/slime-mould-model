from abc import ABC, abstractmethod
from datetime import datetime

from models.models import CryptoResult, time_format


class WorkerBase(ABC):
    def __init__(self, node_id: int, source_currency: str, target_currency: str, start_timestamp: str):
        self.node_id = node_id
        self.source_currency = source_currency.replace(" ", "")
        self.target_currency = target_currency.replace(" ", "")
        self.start_timestamp = start_timestamp
        self.end_timestamp = ""
        self.currency_pair = f'{source_currency}-{target_currency}'
        self.execution_time = 0.0

    @abstractmethod
    def execute(self) -> dict:
        pass

    BASE_URL: str = "https://api.coinbase.com/v2/prices/"
    URL_SUFFIX: str = "/spot/"

    def build_crypto_price_url(self, currency_pair: str) -> str:
        return f'{self.BASE_URL}{currency_pair}{self.URL_SUFFIX}'

    def build_edge_id(self, edge_delimiter: str = ">>", source_node: int = 0) -> str:
        return f'{source_node}{edge_delimiter}{self.node_id}'

    def extract_crypto_result(self, json_response) -> CryptoResult:
        if 'data' in json_response:
            return CryptoResult(
                edge_id=self.build_edge_id(),
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=True,
                amount=float(json_response['data']['amount']),
                error=None
            )
        elif 'error' in json_response:
            return CryptoResult(
                edge_id=self.build_edge_id(),
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=False,
                amount=None,
                error=json_response['error']
            )
        else:
            return CryptoResult(
                edge_id=self.build_edge_id(),
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=False,
                amount=None,
                error="Other error in curl request"
            )

    def set_end_timestamp(self):
        end_timestamp = datetime.now().strftime(time_format)
        self.end_timestamp = end_timestamp

    def add_latency_to_result(self):
        start_time = datetime.strptime(self.start_timestamp, time_format)
        end_time = datetime.strptime(self.end_timestamp, time_format)

        time_taken = end_time - start_time

        print(f"Send timestamp = {self.end_timestamp}. End timestamp = {self.start_timestamp}. Time taken = {time_taken}")
        print(f"Time taken in seconds = {time_taken.total_seconds()} and microseconds {time_taken.microseconds}")

        self.execution_time = time_taken.total_seconds()