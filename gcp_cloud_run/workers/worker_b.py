import requests
import time

from models.crypto_data import CryptoData
from gcp_cloud_run.workers.worker_base import WorkerBase

def aggregate_prices(prices: list[float]) -> float:
    return sum(prices) / len(prices)

class WorkerB(WorkerBase):
    def __init__(
            self,
            source_currency: str,
            target_currency: str,
            number_of_loops: int
    ):
        super().__init__(
            source_currency=source_currency,
            target_currency=target_currency
        )
        self.delay = 5
        self.number_of_loops = number_of_loops
        self.currency_pair = f'{source_currency}-{target_currency}'

    def execute(self) -> CryptoData:
        request_url = self.build_crypto_price_url(self.currency_pair)
        responses = []

        for _ in range(self.number_of_loops):
            response = requests.get(request_url)

            responses.append(response.json())
            time.sleep(self.delay)

        print(responses)
        prices = [float(response['data']['amount']) for response in responses]
        print(prices)
        print(aggregate_prices(prices))

        # TODO: Add error handling

        return CryptoData(
            source_currency=self.source_currency,
            target_currency=self.target_currency,
            price=aggregate_prices(prices)
        )

