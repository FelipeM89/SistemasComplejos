"""
MaquinaOscilador — Maquina de Turing que genera una portadora discreta en su cinta.

MT_OSC: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from turing import MaquinaDeTuring, TuringMachine, FuncionTransicion, TransitionFunction
from codificacion import ESCALA, SCALE, SEP, ALFABETO_SENAL, SIGNAL_ALPHABET, muestras_coseno, cosine_samples


def _construir_maquina_oscilador(nombre: str, n_muestras: int, omega: float) -> MaquinaDeTuring:
    enteros_cos = [round(v * ESCALA) for v in muestras_coseno(n_muestras, omega)]
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

    for k, cos_int in enumerate(enteros_cos):
        digitos = list(str(cos_int))

        primer_estado_digito = q_digito(k, 0)
        cadena.append((q_sep(k), digitos[0], primer_estado_digito))

        for d in range(1, len(digitos)):
            ant = q_digito(k, d - 1)
            act = q_digito(k, d)
            cadena.append((ant, digitos[d], act))

        ultimo_estado_digito = q_digito(k, len(digitos) - 1)
        if k < n_muestras - 1:
            cadena.append((ultimo_estado_digito, SEP, q_sep(k + 1)))
        else:
            q_sep_final = "q_sep_final"
            cadena.append((ultimo_estado_digito, SEP, q_sep_final))
            cadena.append((q_sep_final, "_", q_fin))
            Q.add(q_sep_final)

    for origen, _, destino in cadena:
        Q.add(origen)
        Q.add(destino)

    simbolos_escritos: set[str] = set()
    for origen, sim_escritura, destino in cadena:
        simbolos_escritos.add(sim_escritura)
        for sim_lectura in legibles:
            reglas.append((origen, sim_lectura, destino, sim_escritura, "R"))

    vistas: set[tuple[str, str]] = set()
    reglas_unicas: list[tuple] = []
    for r in reglas:
        clave = (r[0], r[1])
        if clave not in vistas:
            vistas.add(clave)
            reglas_unicas.append(r)

    Sigma = ALFABETO_SENAL
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_"}

    return MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas_unicas),
        estado_inicial=q_inicio,
        estados_finales={q_fin},
        blanco="_",
        max_pasos=n_muestras * 30 + 100,
    )


class MaquinaOscilador:
    """
    MT 2 (Tx) / MT 4 (Rx) — Generador de portadora discreta de coseno.
    """

    def __init__(
        self,
        nombre: str | None = None,
        n_muestras: int | None = None,
        omega: float = 1.0,
        # Alias en ingles
        name: str | None = None,
        n_samples: int | None = None,
    ):
        self.nombre = nombre or name or "MT_OSC"
        self.name = self.nombre
        self.n_muestras = n_muestras if n_muestras is not None else (n_samples if n_samples is not None else 16)
        self.n_samples = self.n_muestras
        self.omega = omega
        self._enteros_cos = [round(v * ESCALA) for v in muestras_coseno(self.n_muestras, omega)]
        self._cos_ints = self._enteros_cos
        self._mt = _construir_maquina_oscilador(self.nombre, self.n_muestras, omega)
        self._tm = self._mt

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT sobre la cinta. Retorna ResultadoEjecucion."""
        return self._mt.ejecutar([SEP], registrar_historial=registrar_historial)

    def run(self, record_history: bool = False):
        return self.ejecutar(registrar_historial=record_history)

    def enteros_portadora(self) -> list[int]:
        """Retorna la lista de enteros Q8 de la portadora."""
        return list(self._enteros_cos)

    def carrier_integers(self) -> list[int]:
        return self.enteros_portadora()

    def describir(self) -> dict:
        return self._mt.describir()

    def describe(self) -> dict:
        return self.describir()


OscillatorMachine = MaquinaOscilador
