import requests
import time

from ..models.models import CryptoResult
from .worker_base import WorkerBase

def aggregate_prices(prices: list[float]) -> float:
    return sum(prices) / len(prices)

def aggregate_output(results: list[CryptoResult]) -> CryptoResult:
    if True in [result.success_response for result in results]:
        success_results = [item for item in results if item.success_response]
        success_prices = [result.amount for result in success_results]
        return CryptoResult(
            edge_id=success_results[0].edge_id,
            source_currency=success_results[0].source_currency,
            target_currency=success_results[0].target_currency,
            currency_pair=success_results[0].currency_pair,
            success_response=True,
            amount=aggregate_prices(success_prices),
            error=None
        )
    else:
        error_messages = list(set([result.error for result in results]))
        delimiter = ". "
        error_string = delimiter.join(error_messages)
        return CryptoResult(
            edge_id=results[0].edge_id,
            source_currency=results[0].source_currency,
            target_currency=results[0].target_currency,
            currency_pair=results[0].currency_pair,
            success_response=False,
            amount=None,
            error=error_string
        )


class WorkerB(WorkerBase):
    def __init__(
            self,
            node_id: int,
            source_currency: str,
            target_currency: str,
            number_of_loops: int = 5,
            delay: int = 5
    ):
        super().__init__(
            node_id=node_id,
            source_currency=source_currency,
            target_currency=target_currency
        )
        self.delay = delay
        self.number_of_loops = number_of_loops

    def execute(self) -> CryptoResult:
        request_url = self.build_crypto_price_url(self.currency_pair)
        crypto_results = []

        for _ in range(self.number_of_loops):
            response = requests.get(request_url)
            crypto_result = self.extract_crypto_result(response.json())

            crypto_results.append(crypto_result)
            time.sleep(self.delay)

        final_result = aggregate_output(crypto_results)
        print("Worker B: execute: completed job.")
        print(final_result)

        return final_result

