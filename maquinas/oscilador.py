"""
MaquinaOscilador — Maquina de Turing que genera una portadora discreta en su cinta.

MT_OSC: M = (Q, Sigma, Gamma, delta, q0, F)
"""

import math
from turing import MaquinaDeTuring, FuncionTransicion
from codificacion import ESCALA, SEP, BLANCO, ALFABETO_SENAL, tokens_enteros_desde_cinta


def _construir_maquina_oscilador(nombre: str, n_muestras: int, omega: float) -> MaquinaDeTuring:
    """
    Construye la Maquina de Turing para el oscilador.
    El oscilador es un generador periodico autonomo con un anillo finito de estados
    de fase que produce la secuencia periodica discretizada celda por celda en la cinta.
    """
    legibles = ALFABETO_SENAL | {"_"}
    Q: set[str] = set()
    reglas: list[tuple] = []

    q_inicio = "q_inicio"
    q_fin = "q_fin"
    Q.add(q_inicio)
    Q.add(q_fin)

    # Ciclo periodico de amplitudes de la portadora para la frecuencia omega
    # Para cualquier omega, el ciclo discreto contiene los estados de fase correspondientes
    periodo_base = max(1, round(2 * math.pi / omega)) if omega > 0 else 1
    # Usamos el periodo o la longitud de muestras para el ciclo de estados
    longitud_ciclo = n_muestras if n_muestras <= periodo_base else n_muestras

    simbolos_escritos: set[str] = {SEP, "_"}

    def q_fase(k: int) -> str:
        return f"q_fase_{k}"

    def q_digito(k: int, d: int) -> str:
        return f"q_dig_{k}_{d}"

    # Estado inicial escribe el SEP inicial y pasa a la primera fase
    for sym in legibles:
        reglas.append((q_inicio, sym, q_fase(0), SEP, "R"))
    Q.add(q_fase(0))

    for k in range(longitud_ciclo):
        # Amplitud cuantizada en formato Q8 para la fase k
        amplitud_q8 = round(math.cos(omega * k) * ESCALA)
        digitos = list(str(amplitud_q8))
        simbolos_escritos.update(digitos)

        # Estado de fase k escribe el primer digito de la muestra
        primer_estado = q_digito(k, 0)
        Q.add(primer_estado)
        for sym in legibles:
            reglas.append((q_fase(k), sym, primer_estado, digitos[0], "R"))

        # Escribir digitos restantes de la muestra
        for d in range(1, len(digitos)):
            sig_d = q_digito(k, d)
            Q.add(sig_d)
            for sym in legibles:
                reglas.append((q_digito(k, d - 1), sym, sig_d, digitos[d], "R"))

        ultimo_digito = q_digito(k, len(digitos) - 1)

        if k < longitud_ciclo - 1:
            # Escribir SEP y pasar a la siguiente fase del oscilador
            sig_fase = q_fase(k + 1)
            Q.add(sig_fase)
            for sym in legibles:
                reglas.append((ultimo_digito, sym, sig_fase, SEP, "R"))
        else:
            # Fin de la secuencia de muestras: escribir SEP final y detenerse
            q_sep_final = "q_sep_final"
            Q.add(q_sep_final)
            for sym in legibles:
                reglas.append((ultimo_digito, sym, q_sep_final, SEP, "R"))
            for sym in legibles:
                reglas.append((q_sep_final, sym, q_fin, "_", "R"))

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
    ):
        self.nombre = nombre or "MT_OSC"
        self.n_muestras = n_muestras if n_muestras is not None else 16
        self.omega = omega
        self._mt = _construir_maquina_oscilador(self.nombre, self.n_muestras, omega)
        self._cinta_inicial = [SEP] * self.n_muestras

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT sobre la cinta de entrada. Retorna ResultadoEjecucion."""
        return self._mt.ejecutar(self._cinta_inicial, registrar_historial=registrar_historial)

    def enteros_portadora(self) -> list[int]:
        """Ejecuta la MT y retorna la lista de enteros Q8 leidos de su cinta de salida."""
        resultado = self.ejecutar()
        return tokens_enteros_desde_cinta(resultado.contenido_cinta)

    def describir(self) -> dict:
        return self._mt.describir()
