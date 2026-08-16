"""
Paquete maquinas — componentes de Maquinas de Turing y canal del sistema.
"""

from .oscilador import MaquinaOscilador
from .multiplicador import MaquinaMultiplicador
from .filtro import MaquinaFiltro
from .canal import Canal, ConfiguracionCanal

__all__ = [
    "MaquinaOscilador",
    "MaquinaMultiplicador",
    "MaquinaFiltro",
    "Canal",
    "ConfiguracionCanal",
]
