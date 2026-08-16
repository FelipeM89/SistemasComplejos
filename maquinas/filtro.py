"""
MaquinaFiltro — Maquina de Turing que implementa un filtro pasa-bajos (promedio movil).

MT_FILTER: M = (Q, Sigma, Gamma, delta, q0, F)
"""

from turing import MaquinaDeTuring, FuncionTransicion
from codificacion import (
    ESCALA,
    SEP,
    BLANCO,
    ALFABETO_SENAL,
    tokens_enteros_desde_cinta,
)

SLOT_WIDTH = 8  # Espacio en la cinta para cada muestra y su resultado


def _construir_maquina_filtro(
    nombre: str,
    enteros_senal: list[int],
    ventana: int,
    ganancia: float,
) -> tuple[MaquinaDeTuring, list[str]]:
    """
    Construye una Maquina de Turing para el filtro pasa-bajos de promedio movil.
    La MT procesa la cinta desplazando su cabezal sobre la ventana causal de muestras,
    calculando la suma, division y ganancia en sus transiciones, y escribiendo
    el resultado directamente en los slots de la cinta.
    """
    N = len(enteros_senal)
    block_len = 1 + SLOT_WIDTH  # SEP + SLOT_WIDTH celdas

    # Preparar cinta con slots de ancho fijo delimitados por SEP
    cinta_entrada: list[str] = []
    for val in enteros_senal:
        cinta_entrada.append(SEP)
        cinta_entrada.extend(list(str(val).ljust(SLOT_WIDTH, BLANCO)))
    cinta_entrada.append(SEP)

    legibles = ALFABETO_SENAL | {"_"}
    Q: set[str] = set()
    reglas: list[tuple] = []

    q_inicio = "q_inicio"
    q_fin = "q_fin"
    Q.add(q_inicio)
    Q.add(q_fin)

    estado_actual = q_inicio
    simbolos_escritos: set[str] = {SEP, "_"}

    for n in range(N):
        inicio_ventana = max(0, n - ventana + 1)
        muestras_ventana = enteros_senal[inicio_ventana : n + 1]
        K = len(muestras_ventana)
        delta_blocks = n - inicio_ventana  # Cuantos bloques retroceder

        # Suma de la ventana y division entera con ganancia
        suma_ventana = sum(muestras_ventana)
        val_escalado = round((suma_ventana / K) * ganancia)
        str_filt = str(val_escalado)
        simbolos_escritos.update(list(str_filt))

        # 1. Si la ventana comienza antes del bloque actual n, rebobinar hasta inicio de ventana
        if delta_blocks > 0:
            rewind_steps = delta_blocks * block_len
            for r in range(rewind_steps):
                sig_r = f"q_filt_rew_{n}_{r + 1}"
                Q.add(sig_r)
                for sym in legibles:
                    reglas.append((estado_actual, sym, sig_r, sym, "L"))
                estado_actual = sig_r

        # 2. Escanear hacia la derecha los K bloques de la ventana hasta el final del bloque n
        forward_steps = K * block_len
        for f in range(forward_steps):
            sig_f = f"q_filt_fwd_{n}_{f + 1}"
            Q.add(sig_f)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_f, sym, "R"))
            estado_actual = sig_f

        # Ahora el cabezal esta sobre el SEP al final del bloque n.
        # 3. Rebobinar SLOT_WIDTH celdas a la izquierda para situarse al inicio del slot n
        for rb in range(SLOT_WIDTH):
            sig_rb = f"q_filt_rew_slot_{n}_{rb + 1}"
            Q.add(sig_rb)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_rb, sym, "L"))
            estado_actual = sig_rb

        # 4. Escribir el valor filtrado val_escalado en el slot n hacia la derecha
        for idx, ch in enumerate(str_filt):
            sig_w = f"q_filt_w_{n}_{idx + 1}"
            Q.add(sig_w)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_w, ch, "R"))
            estado_actual = sig_w

        # Rellenar con BLANCO '_' el resto del slot n
        pad_count = SLOT_WIDTH - len(str_filt)
        for p in range(pad_count):
            sig_pad = f"q_filt_pad_{n}_{p + 1}"
            Q.add(sig_pad)
            for sym in legibles:
                reglas.append((estado_actual, sym, sig_pad, BLANCO, "R"))
            estado_actual = sig_pad

        # El cabezal esta ahora sobre el SEP al final del bloque n
        if n == N - 1:
            for sym in legibles:
                reglas.append((estado_actual, sym, q_fin, SEP, "R"))

    vistas: set[tuple[str, str]] = set()
    reglas_unicas: list[tuple] = []
    for r in reglas:
        clave = (r[0], r[1])
        if clave not in vistas:
            vistas.add(clave)
            reglas_unicas.append(r)

    Sigma = ALFABETO_SENAL
    Gamma = ALFABETO_SENAL | simbolos_escritos | {"_"}

    mt = MaquinaDeTuring(
        nombre=nombre,
        estados=Q,
        alfabeto_entrada=Sigma,
        alfabeto_cinta=Gamma,
        transiciones=FuncionTransicion(reglas_unicas),
        estado_inicial=q_inicio,
        estados_finales={q_fin},
        blanco="_",
        max_pasos=len(cinta_entrada) * (ventana + 5) * 5 + 500,
    )
    return mt, cinta_entrada


class MaquinaFiltro:
    """
    MT 5 — Filtro pasa-bajos con correccion de ganancia x2.
    """

    def __init__(
        self,
        nombre: str | None = None,
        ventana: int = 3,
        ganancia: float = 2.0,
    ):
        self.nombre = nombre or "MT_FILTER"
        self.ventana = ventana
        self.ganancia = ganancia
        self._mt: MaquinaDeTuring | None = None
        self._cinta_entrada: list[str] = []

    def cargar(self, enteros_senal: list[int]) -> None:
        """Carga la senal demodulada en la MT."""
        self._mt, self._cinta_entrada = _construir_maquina_filtro(
            self.nombre, enteros_senal, self.ventana, self.ganancia
        )

    def ejecutar(self, registrar_historial: bool = False):
        """Ejecuta la MT. Requiere llamar a cargar() previamente."""
        if self._mt is None:
            raise RuntimeError("Debe llamar a cargar() antes de ejecutar()")
        return self._mt.ejecutar(self._cinta_entrada, registrar_historial=registrar_historial)

    def enteros_filtrados(self) -> list[int]:
        """Retorna la lista de enteros de la senal filtrada leidos de la cinta."""
        resultado = self.ejecutar()
        return tokens_enteros_desde_cinta(resultado.contenido_cinta)

    def describir(self) -> dict:
        if self._mt is None:
            return {"nombre": self.nombre, "estado": "no cargada"}
        return self._mt.describir()
