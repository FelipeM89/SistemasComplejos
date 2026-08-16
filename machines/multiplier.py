"""
MultiplierMachine — Maquina de Turing que calcula el producto elemento a elemento de dos senales.

MT_MULT: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from maquinas.multiplicador import (
    _construir_maquina_multiplicador,
    MaquinaMultiplicador,
    MultiplierMachine,
)

__all__ = ["_construir_maquina_multiplicador", "MaquinaMultiplicador", "MultiplierMachine"]
