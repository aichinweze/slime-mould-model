from dataclasses import dataclass

@dataclass
class CryptoResult:
    source_currency: str
    target_currency: str
    price: float

@dataclass
class CryptoQueryParams:
    source_currency: str
    target_currency: str
