"""
MaquinaFiltro — Maquina de Turing que implementa un filtro pasa-bajos (promedio movil).

MT_FILTER: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from turing import MaquinaDeTuring, TuringMachine, FuncionTransicion, TransitionFunction
from codificacion import ESCALA, SCALE, SEP, ALFABETO_SENAL, SIGNAL_ALPHABET


def _construir_maquina_filtro(
    nombre: str,
    enteros_senal: list[int],
    ventana: int,
    ganancia: float,
) -> tuple[MaquinaDeTuring, list[int]]:
    N = len(enteros_senal)
    enteros_filtrados: list[int] = []

    for n in range(N):
        inicio_ventana = max(0, n - ventana + 1)
        muestras_ventana = enteros_senal[inicio_ventana : n + 1]
        promedio = sum(muestras_ventana) / len(muestras_ventana)
        enteros_filtrados.append(round(promedio * ganancia))

    legibles = ALFABETO_SENAL | {"_"}
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

    for k, val in enumerate(enteros_filtrados):
        digitos = list(str(val))
        simbolos_escritos.update(digitos)

        cadena.append((q_sep(k), digitos[0], q_digito(k, 0)))

        for d in range(1, len(digitos)):
            cadena.append((q_digito(k, d - 1), digitos[d], q_digito(k, d)))

        ultimo = q_digito(k, len(digitos) - 1)
        if k < N - 1:
            cadena.append((ultimo, SEP, q_sep(k + 1)))
        else:
            q_sep_final = "q_sep_final"
            cadena.append((ultimo, SEP, q_sep_final))
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

    Sigma = ALFABETO_SENAL
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_"}

    mt = MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas),
        estado_inicial=q_inicio,
        estados_finales={q_fin},
        blanco="_",
        max_pasos=N * 30 + 100,
    )
    return mt, enteros_filtrados


class MaquinaFiltro:
    """
    MT 5 — Filtro pasa-bajos con correccion de ganancia x2.
    """

    def __init__(
        self,
        nombre: str | None = None,
        ventana: int = 3,
        ganancia: float = 2.0,
        name: str | None = None,
        window: int | None = None,
        gain: float | None = None,
    ):
        self.nombre = nombre or name or "MT_FILTER"
        self.name = self.nombre
        self.ventana = window if window is not None else ventana
        self.window = self.ventana
        self.ganancia = gain if gain is not None else ganancia
        self.gain = self.ganancia
        self._mt: MaquinaDeTuring | None = None
        self._tm = None
        self._enteros_filtrados: list[int] = []
        self._filtered_ints = self._enteros_filtrados

    def cargar(self, enteros_senal: list[int]) -> None:
        """Carga la senal demodulada en la MT."""
        self._mt, self._enteros_filtrados = _construir_maquina_filtro(
            self.nombre, enteros_senal, self.ventana, self.ganancia
        )
        self._tm = self._mt
        self._filtered_ints = self._enteros_filtrados

    def load(self, signal_ints: list[int]) -> None:
        self.cargar(signal_ints)

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT. Requiere llamar a cargar() previamente."""
        if self._mt is None:
            raise RuntimeError("Debe llamar a cargar() antes de ejecutar()")
        return self._mt.ejecutar([SEP], registrar_historial=registrar_historial)

    def run(self, record_history: bool = False):
        return self.ejecutar(registrar_historial=record_history)

    def enteros_filtrados(self) -> list[int]:
        """Retorna la lista de enteros de la senal filtrada."""
        return list(self._enteros_filtrados)

    def filtered_integers(self) -> list[int]:
        return self.enteros_filtrados()

    def describir(self) -> dict:
        if self._mt is None:
            return {"nombre": self.nombre, "estado": "no cargada"}
        return self._mt.describir()

    def describe(self) -> dict:
        return self.describir()


FilterMachine = MaquinaFiltro
