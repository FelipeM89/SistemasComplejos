"""
SistemaComunicacion — compone las 5 Maquinas de Turing y el canal en una canalizacion completa.
"""

from dataclasses import dataclass, field
from maquinas import (
    MaquinaOscilador,
    MaquinaMultiplicador,
    MaquinaFiltro,
    Canal,
    ConfiguracionCanal,
)
from codificacion import (
    tokens_enteros_desde_cinta,
    ESCALA,
)
from turing import ResultadoEjecucion


@dataclass
class ResultadoEtapa:
    """Resultado de una etapa del sistema de comunicacion."""
    nombre: str
    resultado_mt: ResultadoEjecucion | None
    enteros_senal: list[int]
    descripcion: str

    def senal_flotantes(self) -> list[float]:
        """Convierte los enteros en punto fijo Q8 a valores flotantes."""
        return [v / ESCALA for v in self.enteros_senal]

    def resumen(self) -> str:
        """Resumen textual del resultado de la etapa."""
        if self.resultado_mt:
            return self.resultado_mt.resumen()
        return f"[{self.nombre}] (componente fisico / no-MT)"


@dataclass
class ResultadoSistema:
    """Resultado global de la ejecucion del sistema de comunicacion."""
    senal_entrada: list[float]
    etapas: list[ResultadoEtapa] = field(default_factory=list)

    def senal_salida(self) -> list[float]:
        """Retorna la senal recuperada al final de la canalizacion."""
        return self.etapas[-1].senal_flotantes() if self.etapas else []

    def etapa(self, nombre: str) -> ResultadoEtapa | None:
        """Busca una etapa por su nombre."""
        for e in self.etapas:
            if e.nombre == nombre:
                return e
        return None


class SistemaComunicacion:
    """
    Sistema de comunicacion digital modelado con Maquinas de Turing.
    """

    def __init__(
        self,
        omega_tx: float = 1.0,
        omega_rx: float | None = None,
        ventana_filtro: int = 3,
        config_canal: ConfiguracionCanal | None = None,
    ):
        self.omega_tx = omega_tx
        self.omega_rx = omega_rx if omega_rx is not None else omega_tx
        self.ventana_filtro = ventana_filtro
        self.canal = Canal(config_canal or ConfiguracionCanal())

    def ejecutar(
        self,
        senal_entrada: list[float],
        registrar_historial: bool = False,
    ) -> ResultadoSistema:
        """
        Ejecuta la canalizacion completa del sistema pasando las cintas de una MT a la siguiente.
        """
        N = len(senal_entrada)
        resultado = ResultadoSistema(senal_entrada=senal_entrada)

        enteros_entrada = [round(v * ESCALA) for v in senal_entrada]

        # ── Etapa 1: MT_OSC_TX (MT 2 en el diagrama) ──────────────────
        osc_tx = MaquinaOscilador("MT_OSC_TX", N, self.omega_tx)
        r_osc_tx = osc_tx.ejecutar(registrar_historial)
        enteros_portadora_tx = tokens_enteros_desde_cinta(r_osc_tx.contenido_cinta)
        resultado.etapas.append(ResultadoEtapa(
            nombre="MT_OSC_TX",
            resultado_mt=r_osc_tx,
            enteros_senal=enteros_portadora_tx,
            descripcion="Portadora TX: cos(w*n)",
        ))

        # ── Etapa 2: MT_MULT_TX (MT 1 en el diagrama) ─────────────────
        mult_tx = MaquinaMultiplicador("MT_MULT_TX")
        mult_tx.cargar(enteros_entrada, enteros_portadora_tx)
        r_mult_tx = mult_tx.ejecutar(registrar_historial)
        enteros_modulada = tokens_enteros_desde_cinta(r_mult_tx.contenido_cinta)
        resultado.etapas.append(ResultadoEtapa(
            nombre="MT_MULT_TX",
            resultado_mt=r_mult_tx,
            enteros_senal=enteros_modulada,
            descripcion="Senal modulada: x[n] * cos(w*n)",
        ))

        # ── Etapa 3: CANAL (medio fisico) ─────────────────────────────
        enteros_salida_canal = self.canal.transmitir(enteros_modulada)
        resultado.etapas.append(ResultadoEtapa(
            nombre="CANAL",
            resultado_mt=None,
            enteros_senal=enteros_salida_canal,
            descripcion=f"Canal fisico (modo: {self.canal.configuracion.modo})",
        ))

        # ── Etapa 4: MT_OSC_RX (MT 4 en el diagrama) ──────────────────
        osc_rx = MaquinaOscilador("MT_OSC_RX", N, self.omega_rx)
        r_osc_rx = osc_rx.ejecutar(registrar_historial)
        enteros_portadora_rx = tokens_enteros_desde_cinta(r_osc_rx.contenido_cinta)
        resultado.etapas.append(ResultadoEtapa(
            nombre="MT_OSC_RX",
            resultado_mt=r_osc_rx,
            enteros_senal=enteros_portadora_rx,
            descripcion="Portadora RX: cos(w_rx*n)",
        ))

        # ── Etapa 5: MT_MULT_RX (MT 3 en el diagrama) ─────────────────
        mult_rx = MaquinaMultiplicador("MT_MULT_RX")
        mult_rx.cargar(enteros_salida_canal, enteros_portadora_rx)
        r_mult_rx = mult_rx.ejecutar(registrar_historial)
        enteros_demodulada = tokens_enteros_desde_cinta(r_mult_rx.contenido_cinta)
        resultado.etapas.append(ResultadoEtapa(
            nombre="MT_MULT_RX",
            resultado_mt=r_mult_rx,
            enteros_senal=enteros_demodulada,
            descripcion="Senal demodulada: y[n] * cos(w_rx*n)",
        ))

        # ── Etapa 6: MT_FILTER (MT 5 en el diagrama) ──────────────────
        filtro = MaquinaFiltro("MT_FILTER", ventana=self.ventana_filtro, ganancia=2.0)
        filtro.cargar(enteros_demodulada)
        r_filtro = filtro.ejecutar(registrar_historial)
        enteros_recuperados = tokens_enteros_desde_cinta(r_filtro.contenido_cinta)
        resultado.etapas.append(ResultadoEtapa(
            nombre="MT_FILTER",
            resultado_mt=r_filtro,
            enteros_senal=enteros_recuperados,
            descripcion="Senal recuperada: LPF(demod) * 2 ≈ x[n]",
        ))

        return resultado
