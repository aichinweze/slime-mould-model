import time
import requests

from ..models.models import CryptoResult
from .worker_base import WorkerBase

class WorkerC(WorkerBase):
    def __init__(self, source_currency: str, target_currency: str, delay: int = 15):
        super().__init__(
            source_currency=source_currency,
            target_currency=target_currency
        )
        self.delay = 15

    def execute(self) -> CryptoResult:
        request_url = self.build_crypto_price_url(self.currency_pair)

        response = requests.get(request_url)
        response_json = response.json()
        crypto_result = self.extract_crypto_result(response_json)

        time.sleep(self.delay)

        print("Response status code: " + str(response.status_code))
        print(crypto_result)

        return crypto_result


