"""
OscillatorMachine — Maquina de Turing que genera una portadora discreta en su cinta.

MT_OSC: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from maquinas.oscilador import (
    _construir_maquina_oscilador,
    MaquinaOscilador,
    OscillatorMachine,
)

__all__ = ["_construir_maquina_oscilador", "MaquinaOscilador", "OscillatorMachine"]
