"""
Paquete maquinas — componentes de Maquinas de Turing y canal del sistema.
"""

from .oscilador import MaquinaOscilador, OscillatorMachine
from .multiplicador import MaquinaMultiplicador, MultiplierMachine
from .filtro import MaquinaFiltro, FilterMachine
from .canal import Canal, Channel, ConfiguracionCanal, ChannelConfig

__all__ = [
    "MaquinaOscilador",
    "OscillatorMachine",
    "MaquinaMultiplicador",
    "MultiplierMachine",
    "MaquinaFiltro",
    "FilterMachine",
    "Canal",
    "Channel",
    "ConfiguracionCanal",
    "ChannelConfig",
]
