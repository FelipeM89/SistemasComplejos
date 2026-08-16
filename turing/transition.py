"""
Modulo de transicion (alias de transicion.py para compatibilidad).
"""
from .transicion import (
    FuncionTransicion,
    TransitionFunction,
    ClaveTransicion,
    TransitionKey,
    ValorTransicion,
    TransitionValue,
)

__all__ = [
    "FuncionTransicion",
    "TransitionFunction",
    "ClaveTransicion",
    "TransitionKey",
    "ValorTransicion",
    "TransitionValue",
]
