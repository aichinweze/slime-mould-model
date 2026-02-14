from abc import ABC, abstractmethod

from models.crypto_data import CryptoData


class WorkerBase(ABC):
    def __init__(self, source_currency: str, target_currency: str):
        self.source_currency = source_currency
        self.target_currency = target_currency

    @abstractmethod
    def execute(self) -> CryptoData:
        pass

    BASE_URL: str = "https://api.coinbase.com/v2/prices/"
    URL_SUFFIX: str = "/spot/"

    def build_crypto_price_url(self, currency_pair: str) -> str:
        return f'{self.BASE_URL}{currency_pair}{self.URL_SUFFIX}'
