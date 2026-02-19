from abc import ABC, abstractmethod

from ..models.models import CryptoResult


def convert_crypto_result_to_dict(crypto_result: CryptoResult) -> dict:
    return {
        'source_currency': crypto_result.source_currency,
        'target_currency': crypto_result.target_currency,
        'currency_pair': crypto_result.currency_pair,
        'success_response': crypto_result.success_response,
        'price': crypto_result.amount,
        'error': crypto_result.error
    }

class WorkerBase(ABC):
    def __init__(self, source_currency: str, target_currency: str):
        self.source_currency = source_currency.replace(" ", "")
        self.target_currency = target_currency.replace(" ", "")
        self.currency_pair = f'{source_currency}-{target_currency}'

    @abstractmethod
    def execute(self) -> dict:
        pass

    BASE_URL: str = "https://api.coinbase.com/v2/prices/"
    URL_SUFFIX: str = "/spot/"

    def build_crypto_price_url(self, currency_pair: str) -> str:
        return f'{self.BASE_URL}{currency_pair}{self.URL_SUFFIX}'

    def extract_crypto_result(self, json_response) -> CryptoResult:
        if 'data' in json_response:
            return CryptoResult(
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=True,
                amount=float(json_response['data']['amount']),
                error=None
            )
        elif 'error' in json_response:
            return CryptoResult(
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=False,
                amount=None,
                error=json_response['error']
            )
        else:
            return CryptoResult(
                source_currency=self.source_currency,
                target_currency=self.target_currency,
                currency_pair=self.currency_pair,
                success_response=False,
                amount=None,
                error="Other error in curl request"
            )
