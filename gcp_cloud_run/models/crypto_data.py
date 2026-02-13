from dataclasses import dataclass

@dataclass
class CryptoData:
    source_currency: str
    target_currency: str
    price: float