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
        self.currency_pair = f'{source_currency}-{target_currency}'

    def execute(self) -> dict:
        request_url = self.build_crypto_price_url(self.currency_pair)

        response = requests.get(request_url)
        response_json = response.json()

        time.sleep(self.delay)

        print("Response status code: " + str(response.status_code))
        print(response.json())

        # TODO: Add error handling

        output = CryptoResult(
            source_currency=self.source_currency,
            target_currency=self.target_currency,
            price=float(response_json['data']['amount'])
        )

        return {
            "source_currency": output.source_currency,
            "target_currency": output.target_currency,
            "price": output.price
        }


