"""
Transicion — mapea (estado, simbolo) -> (nuevo_estado, simbolo_escrito, direccion).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaveTransicion:
    estado: str
    simbolo_leido: str

    @property
    def state(self) -> str:
        return self.estado

    @property
    def read_symbol(self) -> str:
        return self.simbolo_leido


@dataclass(frozen=True)
class ValorTransicion:
    siguiente_estado: str
    simbolo_escritura: str
    direccion: str  # "L" o "R"

    @property
    def next_state(self) -> str:
        return self.siguiente_estado

    @property
    def write_symbol(self) -> str:
        return self.simbolo_escritura

    @property
    def direction(self) -> str:
        return self.direccion


class FuncionTransicion:
    """
    Funcion de transicion determinista delta: Q x Gamma -> Q x Gamma x {L, R}.

    Cada regla es: (estado_actual, simbolo_leido) -> (siguiente_estado, simbolo_a_escribir, direccion).
    """

    def __init__(self, reglas: list[tuple] | None = None):
        self._tabla: dict[ClaveTransicion, ValorTransicion] = {}
        if reglas:
            for regla in reglas:
                self.agregar(*regla)

    def agregar(
        self,
        estado: str,
        simbolo_leido: str,
        siguiente_estado: str,
        simbolo_escritura: str,
        direccion: str,
    ) -> None:
        """Registra una nueva regla de transicion."""
        clave = ClaveTransicion(estado, simbolo_leido)
        if clave in self._tabla:
            raise ValueError(f"Transicion duplicada para ({estado!r}, {simbolo_leido!r})")
        self._tabla[clave] = ValorTransicion(siguiente_estado, simbolo_escritura, direccion)

    def add(
        self,
        state: str,
        read_symbol: str,
        next_state: str,
        write_symbol: str,
        direction: str,
    ) -> None:
        self.agregar(state, read_symbol, next_state, write_symbol, direction)

    def aplicar(self, estado: str, simbolo: str) -> ValorTransicion | None:
        """Aplica la transicion correspondiente al estado y simbolo actual."""
        return self._tabla.get(ClaveTransicion(estado, simbolo))

    def apply(self, state: str, symbol: str) -> ValorTransicion | None:
        return self.aplicar(state, symbol)

    def definida_para(self, estado: str, simbolo: str) -> bool:
        """Indica si existe una transicion definida para el par (estado, simbolo)."""
        return ClaveTransicion(estado, simbolo) in self._tabla

    def defined_for(self, state: str, symbol: str) -> bool:
        return self.definida_para(state, symbol)

    def __repr__(self) -> str:
        lineas = [
            f"  ({k.estado}, {k.simbolo_leido!r}) -> ({v.siguiente_estado}, {v.simbolo_escritura!r}, {v.direccion})"
            for k, v in sorted(self._tabla.items(), key=lambda x: x[0].estado)
        ]
        return "FuncionTransicion(\n" + "\n".join(lineas) + "\n)"


TransitionFunction = FuncionTransicion
TransitionKey = ClaveTransicion
TransitionValue = ValorTransicion
