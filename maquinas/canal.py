"""
Canal — modelo computacional del medio de transmision fisico.

El canal NO se modela como una Maquina de Turing.
"""

import random
from dataclasses import dataclass
from codificacion import ESCALA, SCALE


@dataclass
class ConfiguracionCanal:
    """Configuracion de parametros del canal fisico."""
    modo: str = "ideal"          # "ideal" | "noisy" (con ruido) | "attenuated" (atenuado)
    desviacion_ruido: float = 0.0 # desviacion estandar del ruido gaussiano
    atenuacion: float = 1.0       # factor multiplicativo de ganancia/atenuacion
    semilla: int | None = None

    # Compatibilidad con nombres en ingles
    mode: str | None = None
    noise_std: float | None = None
    attenuation: float | None = None
    seed: int | None = None

    def __post_init__(self):
        if self.mode is not None:
            self.modo = self.mode
        else:
            self.mode = self.modo

        if self.noise_std is not None:
            self.desviacion_ruido = self.noise_std
        else:
            self.noise_std = self.desviacion_ruido

        if self.attenuation is not None:
            self.atenuacion = self.attenuation
        else:
            self.attenuation = self.atenuacion

        if self.seed is not None:
            self.semilla = self.seed
        else:
            self.seed = self.semilla


ChannelConfig = ConfiguracionCanal


class Canal:
    """
    Modelo del medio de transmision fisico.
    """

    def __init__(self, configuracion: ConfiguracionCanal | None = None, config: ConfiguracionCanal | None = None):
        self.configuracion = configuracion or config or ConfiguracionCanal()
        self.config = self.configuracion
        self._rng = random.Random(self.configuracion.semilla)

    def transmitir(self, enteros_senal: list[int]) -> list[int]:
        """Aplica la transformacion del medio fisico sobre la lista de enteros Q8."""
        modo = self.configuracion.modo

        if modo == "ideal":
            return list(enteros_senal)

        if modo in ("attenuated", "atenuado"):
            return [round(v * self.configuracion.atenuacion) for v in enteros_senal]

        if modo in ("noisy", "ruido"):
            desv_q8 = self.configuracion.desviacion_ruido * ESCALA
            return [
                round(v + self._rng.gauss(0, desv_q8))
                for v in enteros_senal
            ]

        raise ValueError(f"Modo de canal desconocido: {modo!r}")

    def transmit(self, signal_ints: list[int]) -> list[int]:
        return self.transmitir(signal_ints)

    def describir(self) -> dict:
        return {
            "componente": "Canal",
            "modo": self.configuracion.modo,
            "atenuacion": self.configuracion.atenuacion,
            "desviacion_ruido": self.configuracion.desviacion_ruido,
        }

    def describe(self) -> dict:
        return self.describir()


Channel = Canal
