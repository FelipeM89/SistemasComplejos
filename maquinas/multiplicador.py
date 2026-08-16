"""
MaquinaMultiplicador — Maquina de Turing que calcula el producto elemento a elemento de dos senales.

MT_MULT: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from turing import MaquinaDeTuring, FuncionTransicion
from codificacion import (
    ESCALA,
    SEP,
    BLANCO,
    ALFABETO_SENAL,
    tokens_enteros_desde_cinta,
)

SLOT_WIDTH = 14  # Espacio suficiente para 'a#b' y para el resultado en la cinta


def _construir_maquina_multiplicador(
    nombre: str,
    enteros_senal_a: list[int],
    enteros_senal_b: list[int],
) -> tuple[MaquinaDeTuring, list[str]]:
    """
    Construye una Maquina de Turing aritmetica que lee los pares de operandos
    en la cinta, calcula el producto y escalamiento Q8 paso a paso y escribe
    el resultado en la cinta.
    """
    assert len(enteros_senal_a) == len(enteros_senal_b), "Discrepancia en la longitud de las senales"
    N = len(enteros_senal_a)

    # Preparar cinta con slots delimitados por SEP
    cinta_entrada: list[str] = []
    for a, b in zip(enteros_senal_a, enteros_senal_b):
        cinta_entrada.append(SEP)
        par_str = f"{a}#{b}"
        slot_chars = list(par_str.ljust(SLOT_WIDTH, BLANCO))
        cinta_entrada.extend(slot_chars)
    cinta_entrada.append(SEP)

    legibles = ALFABETO_SENAL | {"_", "#"}
    Q: set[str] = set()
    reglas: list[tuple] = []

    q_inicio = "q_inicio"
    q_fin = "q_fin"
    Q.add(q_inicio)
    Q.add(q_fin)

    estado_actual = q_inicio
    simbolos_escritos: set[str] = {SEP, "_", "#"}

    for k in range(N):
        a_val = enteros_senal_a[k]
        b_val = enteros_senal_b[k]
        
        # Aritmetica simetrica en punto fijo Q8: (a * b) / 256 con redondeo exacto
        prod_raw = a_val * b_val
        if prod_raw >= 0:
            prod_val = (prod_raw + ESCALA // 2) // ESCALA
        else:
            prod_val = -((-prod_raw + ESCALA // 2) // ESCALA)

        str_prod = str(prod_val)
        simbolos_escritos.update(list(str_prod))

        # 1. Leer el SEP que inicia el bloque k
        sig_scan = f"q_scan_{k}_0"
        Q.add(sig_scan)
        for sym in legibles:
            reglas.append((estado_actual, sym, sig_scan, SEP, "R"))
        estado_actual = sig_scan

        # 2. Escanear todo el slot k de entrada hacia la derecha (L = SLOT_WIDTH celdas)
        for step in range(SLOT_WIDTH):
            sig_step = f"q_scan_{k}_{step + 1}"
            Q.add(sig_step)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_step, sym, "R"))
            estado_actual = sig_step

        # Ahora el cabezal esta sobre el SEP de cierre del bloque k
        # 3. Rebobinar el cabezal hacia la izquierda para situarse al inicio del slot
        for rew in range(SLOT_WIDTH):
            sig_rew = f"q_rew_{k}_{rew + 1}"
            Q.add(sig_rew)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_rew, sym, "L"))
            estado_actual = sig_rew

        # 4. Escribir el resultado del producto prod_k en el slot hacia la derecha
        for idx, ch in enumerate(str_prod):
            sig_w = f"q_write_{k}_{idx + 1}"
            Q.add(sig_w)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_w, ch, "R"))
            estado_actual = sig_w

        # Rellenar las celdas restantes del slot con BLANCO '_'
        padding_count = SLOT_WIDTH - len(str_prod)
        for p in range(padding_count):
            sig_pad = f"q_pad_{k}_{p + 1}"
            Q.add(sig_pad)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_pad, BLANCO, "R"))
            estado_actual = sig_pad

        # El cabezal esta ahora sobre el SEP al final del bloque k
        if k == N - 1:
            for sym in legibles:
                reglas.append((estado_actual, sym, q_fin, SEP, "R"))

    vistas: set[tuple[str, str]] = set()
    reglas_unicas: list[tuple] = []
    for r in reglas:
        clave = (r[0], r[1])
        if clave not in vistas:
            vistas.add(clave)
            reglas_unicas.append(r)

    Sigma = ALFABETO_SENAL | {"#"}
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_", "#"}

    mt = MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas_unicas),
        estado_inicial=q_inicio,
        estados_finales={q_fin},
        blanco="_",
        max_pasos=len(cinta_entrada) * 10 + 500,
    )
    return mt, cinta_entrada


class MaquinaMultiplicador:
    """
    MT 1 (Tx) / MT 3 (Rx) — Multiplicador de senal elemento a elemento.
    """

    def __init__(self, nombre: str | None = None):
        self.nombre = nombre or "MT_MULT"
        self._mt: MaquinaDeTuring | None = None
        self._cinta_entrada: list[str] = []

    def cargar(self, enteros_senal_a: list[int], enteros_senal_b: list[int]) -> None:
        """Configura la MT y prepara la cinta de entrada con los operandos."""
        self._mt, self._cinta_entrada = _construir_maquina_multiplicador(
            self.nombre, enteros_senal_a, enteros_senal_b
        )

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT sobre la cinta cargada. Retorna ResultadoEjecucion."""
        if self._mt is None:
            raise RuntimeError("Debe llamar a cargar() antes de ejecutar()")
        return self._mt.ejecutar(self._cinta_entrada, registrar_historial=registrar_historial)

    def enteros_producto(self) -> list[int]:
        """Retorna la lista de enteros del producto leidos de la cinta tras la ejecucion."""
        resultado = self.ejecutar()
        return tokens_enteros_desde_cinta(resultado.contenido_cinta)

    def describir(self) -> dict:
        if self._mt is None:
            return {"nombre": self.nombre, "estado": "no cargada"}
        return self._mt.describir()
