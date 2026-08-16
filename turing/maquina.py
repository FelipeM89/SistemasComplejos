"""
MaquinaDeTuring — motor generico de Maquina de Turing determinista.

Definicion formal: M = (Q, Sigma, Gamma, delta, q0, F)

  Q     — conjunto finito de estados
  Sigma — alfabeto de entrada (subconjunto de Gamma, sin el simbolo blanco)
  Gamma — alfabeto de cinta (Sigma union {blanco} union simbolos auxiliares)
  delta — funcion de transicion (FuncionTransicion)
  q0    — estado inicial
  F     — conjunto de estados de aceptacion / parada
"""

from dataclasses import dataclass, field
from typing import Any
from .cinta import Cinta, BLANCO, BLANK
from .transicion import FuncionTransicion, TransitionFunction


@dataclass
class Configuracion:
    """Configuracion instantanea de la Maquina de Turing (paso, estado, cabezal, cinta)."""
    paso: int
    estado: str
    cabezal: int
    captura_cinta: dict

    @property
    def step(self) -> int:
        return self.paso

    @property
    def state(self) -> str:
        return self.estado

    @property
    def head(self) -> int:
        return self.cabezal

    @property
    def tape_snapshot(self) -> dict:
        return self.captura_cinta


Configuration = Configuracion


@dataclass
class ResultadoEjecucion:
    """Resultado de la ejecucion de una Maquina de Turing."""
    nombre_maquina: str
    estado_inicial: str
    estado_final: str
    aceptada: bool
    pasos: int
    contenido_cinta: list[str]
    historial: list[Configuracion] = field(default_factory=list)

    @property
    def machine_name(self) -> str:
        return self.nombre_maquina

    @property
    def initial_state(self) -> str:
        return self.estado_inicial

    @property
    def final_state(self) -> str:
        return self.estado_final

    @property
    def accepted(self) -> bool:
        return self.aceptada

    @property
    def steps(self) -> int:
        return self.pasos

    @property
    def tape_content(self) -> list[str]:
        return self.contenido_cinta

    @property
    def history(self) -> list[Configuracion]:
        return self.historial

    def resumen(self) -> str:
        estado_str = "ACEPTADA" if self.aceptada else "DETENIDA"
        return (
            f"[{self.nombre_maquina}] {estado_str} | "
            f"q0={self.estado_inicial!r} -> qf={self.estado_final!r} | "
            f"pasos={self.pasos}"
        )

    def summary(self) -> str:
        return self.resumen()


ExecutionResult = ResultadoEjecucion


class MaquinaDeTuring:
    """
    Maquina de Turing determinista generica.

    Parametros
    ----------
    nombre              : identificador legible (ej. "MT_OSC_TX")
    estados             : conjunto completo de estados Q
    alfabeto_entrada    : alfabeto de entrada Sigma
    alfabeto_cinta      : alfabeto de cinta Gamma (debe incluir blanco y todo Sigma)
    transiciones        : funcion de transicion delta
    estado_inicial      : estado inicial q0
    estados_finales     : conjunto de estados finales/aceptacion F
    blanco              : simbolo blanco (por defecto "_")
    max_pasos           : limite maximo de pasos para prevenir ciclos infinitos
    """

    def __init__(
        self,
        name: str | None = None,
        states: set[str] | None = None,
        input_alpha: set[str] | None = None,
        tape_alpha: set[str] | None = None,
        transitions: FuncionTransicion | None = None,
        initial: str | None = None,
        final: set[str] | None = None,
        blank: str = BLANCO,
        max_steps: int = 100_000,
        # Argumentos en espanol
        nombre: str | None = None,
        estados: set[str] | None = None,
        alfabeto_entrada: set[str] | None = None,
        alfabeto_cinta: set[str] | None = None,
        transiciones: FuncionTransicion | None = None,
        estado_inicial: str | None = None,
        estados_finales: set[str] | None = None,
        blanco: str = BLANCO,
        max_pasos: int = 100_000,
    ):
        self.nombre = nombre or name or "MT"
        self.name = self.nombre
        self.Q = estados if estados is not None else (states if states is not None else set())
        self.Sigma = alfabeto_entrada if alfabeto_entrada is not None else (input_alpha if input_alpha is not None else set())
        self.Gamma = alfabeto_cinta if alfabeto_cinta is not None else (tape_alpha if tape_alpha is not None else set())
        self.delta = transiciones if transiciones is not None else transitions
        self.q0 = estado_inicial or initial or ""
        self.F = estados_finales if estados_finales is not None else (final if final is not None else set())
        self.blanco = blanco or blank
        self.blank = self.blanco
        self.max_pasos = max_pasos or max_steps
        self.max_steps = self.max_pasos

        self._validar()

    def _validar(self) -> None:
        assert self.q0 in self.Q, f"{self.nombre}: estado inicial {self.q0!r} no pertenece a Q"
        assert self.F.issubset(self.Q), f"{self.nombre}: F no es subconjunto de Q"
        assert self.blanco in self.Gamma, f"{self.nombre}: el simbolo blanco no pertenece a Gamma"
        assert self.Sigma.issubset(self.Gamma), f"{self.nombre}: Sigma no es subconjunto de Gamma"

    def ejecutar(
        self,
        simbolos_entrada: list[str],
        registrar_historial: bool = False,
    ) -> ResultadoEjecucion:
        """
        Carga la cinta con los simbolos de entrada y ejecuta la maquina hasta detenerse.
        """
        cinta = Cinta(simbolos_entrada, blanco=self.blanco)
        estado_actual = self.q0
        pasos = 0
        historial: list[Configuracion] = []

        if registrar_historial:
            historial.append(Configuracion(0, estado_actual, cinta.cabezal, cinta.captura()))

        while estado_actual not in self.F:
            if pasos >= self.max_pasos:
                raise RuntimeError(
                    f"{self.nombre}: supero el limite de {self.max_pasos} pasos (posible bucle infinito)"
                )

            simbolo_leido = cinta.leer()
            transicion = self.delta.aplicar(estado_actual, simbolo_leido)

            if transicion is None:
                break  # parada por transicion no definida

            cinta.escribir(transicion.simbolo_escritura)
            cinta.mover(transicion.direccion)
            estado_actual = transicion.siguiente_estado
            pasos += 1

            if registrar_historial:
                historial.append(Configuracion(pasos, estado_actual, cinta.cabezal, cinta.captura()))

        return ResultadoEjecucion(
            nombre_maquina=self.nombre,
            estado_inicial=self.q0,
            estado_final=estado_actual,
            aceptada=estado_actual in self.F,
            pasos=pasos,
            contenido_cinta=cinta.contenido(),
            historial=historial,
        )

    def run(
        self,
        input_symbols: list[str],
        record_history: bool = False,
    ) -> ResultadoEjecucion:
        return self.ejecutar(input_symbols, registrar_historial=record_history)

    def describir(self) -> dict[str, Any]:
        """Retorna la tupla formal y componentes de la maquina en formato diccionario."""
        return {
            "nombre": self.nombre,
            "Q": sorted(self.Q),
            "Sigma": sorted(self.Sigma),
            "Gamma": sorted(self.Gamma),
            "q0": self.q0,
            "F": sorted(self.F),
            "blanco": self.blanco,
        }

    def describe(self) -> dict[str, Any]:
        return self.describir()


TuringMachine = MaquinaDeTuring
