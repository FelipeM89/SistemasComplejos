"""
Modulo de maquina (alias de maquina.py para compatibilidad).
"""
from .maquina import (
    MaquinaDeTuring,
    TuringMachine,
    ResultadoEjecucion,
    ExecutionResult,
    Configuracion,
    Configuration,
)

__all__ = [
    "MaquinaDeTuring",
    "TuringMachine",
    "ResultadoEjecucion",
    "ExecutionResult",
    "Configuracion",
    "Configuration",
]
