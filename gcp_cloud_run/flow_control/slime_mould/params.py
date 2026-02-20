
from dataclasses import dataclass

@dataclass
class SlimeMouldParams:
    alpha: float
    mu: float
    epsilon: float
    d_max: float
    d_min: float