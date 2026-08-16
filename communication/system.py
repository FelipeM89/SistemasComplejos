"""
CommunicationSystem — compone las 5 Maquinas de Turing y el canal en una canalizacion completa.

Flujo de la canalizacion:
    SENAL DE ENTRADA x[n]
        |
    [MT_OSC_TX]  genera cos(w*n) en cinta
        | portadora_tx
    [MT_MULT_TX] calcula x[n] * portadora_tx[n] -> modulada[n]
        |
    [CANAL]      medio fisico y[n] = H(modulada[n])
        |
    [MT_OSC_RX]  genera cos(w_rx*n) en cinta
        | portadora_rx
    [MT_MULT_RX] calcula y[n] * portadora_rx[n] -> demodulada[n]
        |
    [MT_FILTER]  calcula LPF(demodulada[n]) * 2 -> recuperada[n]
        |
    SENAL RECUPERADA x^[n]

El paso de datos entre maquinas se realiza mediante la cinta de simbolos de cada MT.
"""

from dataclasses import dataclass, field
from typing import Any

from machines import (
    OscillatorMachine,
    MultiplierMachine,
    FilterMachine,
    Channel,
    ChannelConfig,
)
from encoding import (
    encode_signal,
    decode_signal,
    integer_tokens_from_tape,
    SCALE,
)
from turing import ExecutionResult


@dataclass
class StageResult:
    """Resultado de una etapa del sistema de comunicacion."""
    name: str
    tm_result: ExecutionResult | None
    signal_ints: list[int]
    description: str

    def signal_floats(self) -> list[float]:
        """Convierte los enteros en punto fijo Q8 a valores flotantes."""
        return [v / SCALE for v in self.signal_ints]

    def summary(self) -> str:
        """Resumen textual del resultado de la etapa."""
        if self.tm_result:
            return self.tm_result.summary()
        return f"[{self.name}] (componente fisico / no-MT)"


@dataclass
class SystemResult:
    """Resultado global de la ejecucion del sistema de comunicacion."""
    input_signal: list[float]
    stages: list[StageResult] = field(default_factory=list)

    def output_signal(self) -> list[float]:
        """Retorna la senal recuperada al final de la canalizacion."""
        return self.stages[-1].signal_floats() if self.stages else []

    def stage(self, name: str) -> StageResult | None:
        """Busca una etapa por su nombre."""
        for s in self.stages:
            if s.name == name:
                return s
        return None


class CommunicationSystem:
    """
    Sistema de comunicacion digital modelado con Maquinas de Turing.

    Parametros
    ----------
    omega_tx      : frecuencia angular de la portadora del transmisor (rad/muestra)
    omega_rx      : frecuencia angular de la portadora del receptor (por defecto igual a omega_tx)
    filter_window : tamano de la ventana del filtro pasa-bajos de promedio movil
    channel_cfg   : configuracion del modelo de canal fisico
    """

    def __init__(
        self,
        omega_tx: float = 1.0,
        omega_rx: float | None = None,
        filter_window: int = 3,
        channel_cfg: ChannelConfig | None = None,
    ):
        self.omega_tx = omega_tx
        self.omega_rx = omega_rx if omega_rx is not None else omega_tx
        self.filter_window = filter_window
        self.channel = Channel(channel_cfg or ChannelConfig())

    # ------------------------------------------------------------------
    # Canalizacion principal
    # ------------------------------------------------------------------

    def run(
        self,
        input_signal: list[float],
        record_history: bool = False,
    ) -> SystemResult:
        """
        Ejecuta la canalizacion completa del sistema.

        Parametros
        ----------
        input_signal   : muestras discretas x[n] en [-1, 1]
        record_history : si cada MT debe registrar el historial paso a paso

        Retorna
        -------
        SystemResult con los resultados de cada etapa y la senal recuperada.
        """
        N = len(input_signal)
        result = SystemResult(input_signal=input_signal)

        input_ints = [round(v * SCALE) for v in input_signal]

        # ── Etapa 1: MT_OSC_TX (MT 2 en el diagrama de clase) ─────────
        osc_tx = OscillatorMachine("MT_OSC_TX", N, self.omega_tx)
        r_osc_tx = osc_tx.run(record_history)
        carrier_tx_ints = integer_tokens_from_tape(r_osc_tx.tape_content)
        result.stages.append(StageResult(
            name="MT_OSC_TX",
            tm_result=r_osc_tx,
            signal_ints=carrier_tx_ints,
            description="Portadora TX: cos(w*n)",
        ))

        # ── Etapa 2: MT_MULT_TX (MT 1 en el diagrama de clase) ────────
        mult_tx = MultiplierMachine("MT_MULT_TX")
        mult_tx.load(input_ints, carrier_tx_ints)
        r_mult_tx = mult_tx.run(record_history)
        modulated_ints = integer_tokens_from_tape(r_mult_tx.tape_content)
        result.stages.append(StageResult(
            name="MT_MULT_TX",
            tm_result=r_mult_tx,
            signal_ints=modulated_ints,
            description="Senal modulada: x[n] * cos(w*n)",
        ))

        # ── Etapa 3: CANAL (medio fisico) ─────────────────────────────
        channel_out_ints = self.channel.transmit(modulated_ints)
        result.stages.append(StageResult(
            name="CANAL",
            tm_result=None,
            signal_ints=channel_out_ints,
            description=f"Canal fisico (modo: {self.channel.config.mode})",
        ))

        # ── Etapa 4: MT_OSC_RX (MT 4 en el diagrama de clase) ─────────
        osc_rx = OscillatorMachine("MT_OSC_RX", N, self.omega_rx)
        r_osc_rx = osc_rx.run(record_history)
        carrier_rx_ints = integer_tokens_from_tape(r_osc_rx.tape_content)
        result.stages.append(StageResult(
            name="MT_OSC_RX",
            tm_result=r_osc_rx,
            signal_ints=carrier_rx_ints,
            description="Portadora RX: cos(w_rx*n)",
        ))

        # ── Etapa 5: MT_MULT_RX (MT 3 en el diagrama de clase) ────────
        mult_rx = MultiplierMachine("MT_MULT_RX")
        mult_rx.load(channel_out_ints, carrier_rx_ints)
        r_mult_rx = mult_rx.run(record_history)
        demodulated_ints = integer_tokens_from_tape(r_mult_rx.tape_content)
        result.stages.append(StageResult(
            name="MT_MULT_RX",
            tm_result=r_mult_rx,
            signal_ints=demodulated_ints,
            description="Senal demodulada: y[n] * cos(w_rx*n)",
        ))

        # ── Etapa 6: MT_FILTER (MT 5 en el diagrama de clase) ─────────
        filt = FilterMachine("MT_FILTER", window=self.filter_window, gain=2.0)
        filt.load(demodulated_ints)
        r_filt = filt.run(record_history)
        filtered_ints = integer_tokens_from_tape(r_filt.tape_content)
        result.stages.append(StageResult(
            name="MT_FILTER",
            tm_result=r_filt,
            signal_ints=filtered_ints,
            description="Senal recuperada: LPF(demod) * 2 ≈ x[n]",
        ))

        return result
