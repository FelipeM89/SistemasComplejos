"""
Canal — modelo computacional del medio de transmision fisico.

El canal NO se modela como una Maquina de Turing.

Justificacion teorica:
──────────────────────
Un canal fisico no es un dispositivo computacional de procesamiento simbolico,
sino un medio de propagacion. En teoria de la comunicacion (Shannon), el canal
se modela como una transformacion fisica y/o estocastica y = H(x) + n.

Separar el canal de las Maquinas de Turing preserva el rigor academico:
los bloques de computo (MTs) se diferencian claramente del medio fisico.
"""

import random
from dataclasses import dataclass
from encoding import SCALE


@dataclass
class ChannelConfig:
    """Configuracion de parametros del canal fisico."""
    mode: str = "ideal"         # "ideal" | "noisy" (con ruido) | "attenuated" (atenuado)
    noise_std: float = 0.0      # desviacion estandar del ruido gaussiano
    attenuation: float = 1.0    # factor multiplicativo de ganancia/atenuacion
    seed: int | None = None


class Channel:
    """
    Modelo del medio de transmision fisico.

    Transforma los enteros en punto fijo Q8 transmitidos hacia el receptor.

    Modos disponibles:
      ideal      — canal sin perdidas ni distorsion (identidad)
      noisy      — anade ruido gaussiano
      attenuated — aplica atenuacion de amplitud
    """

    def __init__(self, config: ChannelConfig | None = None):
        self.config = config or ChannelConfig()
        self._rng = random.Random(self.config.seed)

    def transmit(self, signal_ints: list[int]) -> list[int]:
        """Aplica la transformacion del medio fisico sobre la lista de enteros Q8."""
        mode = self.config.mode

        if mode == "ideal":
            return list(signal_ints)

        if mode == "attenuated":
            return [round(v * self.config.attenuation) for v in signal_ints]

        if mode == "noisy":
            std_q8 = self.config.noise_std * SCALE
            return [
                round(v + self._rng.gauss(0, std_q8))
                for v in signal_ints
            ]

        raise ValueError(f"Modo de canal desconocido: {self.config.mode!r}")

    def describe(self) -> dict:
        """Retorna los parametros descriptivos del canal."""
        return {
            "componente": "Canal",
            "modo": self.config.mode,
            "atenuacion": self.config.attenuation,
            "desviacion_ruido": self.config.noise_std,
        }
