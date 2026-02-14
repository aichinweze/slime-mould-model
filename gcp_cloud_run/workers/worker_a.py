import time
import requests

from models.crypto_data import CryptoData
from gcp_cloud_run.workers.worker_base import WorkerBase

class WorkerA(WorkerBase):
    def __init__(self, source_currency: str, target_currency: str):
        super().__init__(
            source_currency=source_currency,
            target_currency=target_currency
        )
        self.delay = 1
        self.currency_pair = f'{source_currency}-{target_currency}'

    def execute(self) -> CryptoData:
        request_url = self.build_crypto_price_url(self.currency_pair)

        response = requests.get(request_url)
        response_json = response.json()

        time.sleep(self.delay)

        print("Response status code: " + str(response.status_code))
        print(response.json())

        # TODO: Add error handling

        return CryptoData(
            source_currency=self.source_currency,
            target_currency=self.target_currency,
            price=float(response_json['data']['amount'])
        )


