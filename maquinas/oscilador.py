"""
MaquinaOscilador — Maquina de Turing que genera una portadora discreta en su cinta.

MT_OSC: M = (Q, Sigma, Gamma, delta, q0, F)
"""

import math
from turing import MaquinaDeTuring, TuringMachine, FuncionTransicion, TransitionFunction
from codificacion import ESCALA, SCALE, SEP, ALFABETO_SENAL, SIGNAL_ALPHABET, muestras_coseno, cosine_samples


def _construir_maquina_oscilador(nombre: str, n_muestras: int, omega: float) -> MaquinaDeTuring:
    """
    Construye la Maquina de Turing para el oscilador.
    El oscilador es un generador periodico autonomo modelado como una MT.
    Sus transiciones definen el ciclo de estados de fase que genera la
    forma de onda discreta muestreada en formato Q8 celda por celda en la cinta.
    """
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

    for k in range(n_muestras):
        # Cada estado de fase k produce su amplitud Q8 discreta: round(cos(w*k) * ESCALA)
        val_k = round(math.cos(omega * k) * ESCALA)
        digitos = list(str(val_k))
        simbolos_escritos.update(digitos)

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

    vistas: set[tuple[str, str]] = set()
    for origen, sim_escritura, destino in cadena:
        for sim_lectura in legibles:
            clave = (origen, sim_lectura)
            if clave not in vistas:
                vistas.add(clave)
                reglas.append((origen, sim_lectura, destino, sim_escritura, "R"))

    Sigma = ALFABETO_SENAL
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_"}

    return MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas),
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
        name: str | None = None,
        n_samples: int | None = None,
    ):
        self.nombre = nombre or name or "MT_OSC"
        self.name = self.nombre
        self.n_muestras = n_muestras if n_muestras is not None else (n_samples if n_samples is not None else 16)
        self.n_samples = self.n_muestras
        self.omega = omega
        self._mt = _construir_maquina_oscilador(self.nombre, self.n_muestras, omega)
        self._tm = self._mt
        self._cinta_inicial = [SEP] * self.n_muestras

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT sobre la cinta de entrada. Retorna ResultadoEjecucion."""
        return self._mt.ejecutar(self._cinta_inicial, registrar_historial=registrar_historial)

    def run(self, record_history: bool = False):
        return self.ejecutar(registrar_historial=record_history)

    def enteros_portadora(self) -> list[int]:
        """Ejecuta la MT y retorna la lista de enteros Q8 leidos de su cinta de salida."""
        resultado = self.ejecutar()
        from codificacion import tokens_enteros_desde_cinta
        return tokens_enteros_desde_cinta(resultado.contenido_cinta)

    def carrier_integers(self) -> list[int]:
        return self.enteros_portadora()

    def describir(self) -> dict:
        return self._mt.describir()

    def describe(self) -> dict:
        return self.describir()


OscillatorMachine = MaquinaOscilador
