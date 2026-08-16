"""
Paquete turing — motor generico de Maquinas de Turing.
"""

from .cinta import Cinta, Tape, BLANCO, BLANK
from .transicion import (
    FuncionTransicion,
    TransitionFunction,
    ClaveTransicion,
    TransitionKey,
    ValorTransicion,
    TransitionValue,
)
from .maquina import (
    MaquinaDeTuring,
    TuringMachine,
    ResultadoEjecucion,
    ExecutionResult,
    Configuracion,
    Configuration,
)

__all__ = [
    "Cinta",
    "Tape",
    "BLANCO",
    "BLANK",
    "FuncionTransicion",
    "TransitionFunction",
    "ClaveTransicion",
    "TransitionKey",
    "ValorTransicion",
    "TransitionValue",
    "MaquinaDeTuring",
    "TuringMachine",
    "ResultadoEjecucion",
    "ExecutionResult",
    "Configuracion",
    "Configuration",
]
