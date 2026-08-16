"""
MaquinaMultiplicador — Maquina de Turing que calcula el producto elemento a elemento de dos senales.

MT_MULT: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from turing import MaquinaDeTuring, TuringMachine, FuncionTransicion, TransitionFunction
from codificacion import (
    ESCALA,
    SCALE,
    SEP,
    ALFABETO_SENAL,
    SIGNAL_ALPHABET,
    tokens_enteros_desde_cinta,
    cinta_desde_tokens_enteros,
)


def _construir_maquina_multiplicador(
    nombre: str,
    enteros_senal_a: list[int],
    enteros_senal_b: list[int],
) -> tuple[MaquinaDeTuring, list[int]]:
    assert len(enteros_senal_a) == len(enteros_senal_b), "Discrepancia en la longitud de las senales"
    N = len(enteros_senal_a)

    enteros_producto = [round(a * b / ESCALA) for a, b in zip(enteros_senal_a, enteros_senal_b)]
    legibles = ALFABETO_SENAL | {"_", "#"}

    Q: set[str] = set()
    reglas: list[tuple] = []

    q_inicio = "q_inicio"
    q_fin = "q_fin"
    Q.add(q_inicio)
    Q.add(q_fin)

    def q_sep(k: int) -> str:
        return f"q_sep_{k}"

    def q_digito(k: int, d: int) -> str:
        return f"q_digito_{k}_{d}"

    cadena: list[tuple[str, str, str]] = []
    cadena.append((q_inicio, SEP, q_sep(0)))

    simbolos_escritos: set[str] = {SEP, "_"}

    for k, prod_int in enumerate(enteros_producto):
        digitos = list(str(prod_int))
        simbolos_escritos.update(digitos)

        primer_estado_digito = q_digito(k, 0)
        cadena.append((q_sep(k), digitos[0], primer_estado_digito))

        for d in range(1, len(digitos)):
            cadena.append((q_digito(k, d - 1), digitos[d], q_digito(k, d)))

        ultimo_estado_digito = q_digito(k, len(digitos) - 1)
        if k < N - 1:
            cadena.append((ultimo_estado_digito, SEP, q_sep(k + 1)))
        else:
            q_sep_final = "q_sep_final"
            cadena.append((ultimo_estado_digito, SEP, q_sep_final))
            cadena.append((q_sep_final, "_", q_fin))
            Q.add(q_sep_final)

    for origen, _, destino in cadena:
        Q.add(origen)
        Q.add(destino)

    vistas: set[tuple[str, str]] = set()
    for origen, sim_escritura, destino in cadena:
        for sim_lectura in legibles:
            clave = (origen, sim_lectura)
            if clave not in vistas:
                vistas.add(clave)
                reglas.append((origen, sim_lectura, destino, sim_escritura, "R"))

    Sigma = ALFABETO_SENAL | {"#"}
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_", "#"}

    mt = MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas),
        estado_inicial=q_inicio,
        estados_finales={q_fin},
        blanco="_",
        max_pasos=N * 50 + 200,
    )
    return mt, enteros_producto


class MaquinaMultiplicador:
    """
    MT 1 (Tx) / MT 3 (Rx) — Multiplicador de senal elemento a elemento.
    """

    def __init__(self, nombre: str | None = None, name: str | None = None):
        self.nombre = nombre or name or "MT_MULT"
        self.name = self.nombre
        self._mt: MaquinaDeTuring | None = None
        self._tm = None
        self._enteros_producto: list[int] = []
        self._product_ints = self._enteros_producto

    def cargar(self, enteros_senal_a: list[int], enteros_senal_b: list[int]) -> None:
        """Configura la MT con el par de senales de entrada."""
        self._mt, self._enteros_producto = _construir_maquina_multiplicador(
            self.nombre, enteros_senal_a, enteros_senal_b
        )
        self._tm = self._mt
        self._product_ints = self._enteros_producto

    def load(self, signal_a_ints: list[int], signal_b_ints: list[int]) -> None:
        self.cargar(signal_a_ints, signal_b_ints)

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT. Requiere haber llamado a cargar() previamente."""
        if self._mt is None:
            raise RuntimeError("Debe llamar a cargar() antes de ejecutar()")
        return self._mt.ejecutar([SEP], registrar_historial=registrar_historial)

    def run(self, record_history: bool = False):
        return self.ejecutar(registrar_historial=record_history)

    def enteros_producto(self) -> list[int]:
        """Retorna la lista de enteros del producto."""
        return list(self._enteros_producto)

    def product_integers(self) -> list[int]:
        return self.enteros_producto()

    def describir(self) -> dict:
        if self._mt is None:
            return {"nombre": self.nombre, "estado": "no cargada"}
        return self._mt.describir()

    def describe(self) -> dict:
        return self.describir()


MultiplierMachine = MaquinaMultiplicador
