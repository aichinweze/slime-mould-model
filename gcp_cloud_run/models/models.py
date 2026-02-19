from dataclasses import dataclass

@dataclass
class CryptoResult:
    source_currency: str
    target_currency: str
    currency_pair: str
    success_response: bool
    amount: float | None
    error: str | None

@dataclass
class CryptoQueryParams:
    source_currency: str
    target_currency: str
