"""
FilterMachine — Maquina de Turing que implementa un filtro pasa-bajos (promedio movil).

MT_FILTER: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from maquinas.filtro import (
    _construir_maquina_filtro,
    MaquinaFiltro,
    FilterMachine,
)

__all__ = ["_construir_maquina_filtro", "MaquinaFiltro", "FilterMachine"]
