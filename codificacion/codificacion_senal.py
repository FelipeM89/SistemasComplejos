"""
Codificacion y decodificacion de senales para cintas de Maquinas de Turing.

── Diseno de la representacion ────────────────────────────────────────────────

Las senales continuas x(t) y cos(w*t) se discretizan en N muestras. Cada valor
de muestra se mapea a un entero de punto fijo en formato Q:

    codificado = round(valor * ESCALA)        (entero)

ESCALA = 2**PRECISION  (por defecto PRECISION=8 -> ESCALA=256)
"""

import math

PRECISION: int = 8               # bits de precision fraccionaria
ESCALA: int = 2 ** PRECISION     # 256
SCALE = ESCALA

SEP: str = "|"
DIGITOS: set[str] = set("0123456789")
DIGITS = DIGITOS
SIGNO: str = "-"
SIGN = SIGNO
BLANCO: str = "_"
BLANK = BLANCO

ALFABETO_SENAL: set[str] = DIGITOS | {SIGNO, SEP, BLANCO}
SIGNAL_ALPHABET = ALFABETO_SENAL


# ── Codificacion ─────────────────────────────────────────────────────────────

def codificar_muestra(valor: float) -> list[str]:
    """Float -> lista de simbolos de cinta que representan una muestra."""
    entero = round(valor * ESCALA)
    return list(str(entero))


encode_sample = codificar_muestra


def codificar_senal(muestras: list[float]) -> list[str]:
    """
    Lista de flotantes -> lista plana de simbolos para la cinta.

    Formato: SEP v0 SEP v1 SEP ... SEP v_{n-1} SEP
    """
    cinta: list[str] = []
    for m in muestras:
        cinta.append(SEP)
        cinta.extend(codificar_muestra(m))
    cinta.append(SEP)
    return cinta


encode_signal = codificar_senal


# ── Decodificacion ───────────────────────────────────────────────────────────

def _analizar_tokens_cinta(simbolos_cinta: list[str]) -> list[str]:
    """Divide el contenido de la cinta por SEP y descarta tokens vacios o blancos."""
    contenido = "".join(simbolos_cinta)
    return [t for t in contenido.split(SEP) if t and t != BLANCO]


_parse_tape_tokens = _analizar_tokens_cinta


def decodificar_muestra(token: str) -> float:
    """Token de cinta (cadena de digitos) -> valor float."""
    return int(token) / ESCALA


decode_sample = decodificar_muestra


def decodificar_senal(simbolos_cinta: list[str]) -> list[float]:
    """Lista plana de simbolos de cinta -> lista de flotantes decodificados."""
    return [decodificar_muestra(t) for t in _analizar_tokens_cinta(simbolos_cinta)]


decode_signal = decodificar_senal


# ── Utilidades para las Maquinas de Turing ───────────────────────────────────

def tokens_enteros_desde_cinta(simbolos_cinta: list[str]) -> list[int]:
    """Extrae los valores enteros codificados (sin dividir por ESCALA)."""
    return [int(t) for t in _analizar_tokens_cinta(simbolos_cinta)]


integer_tokens_from_tape = tokens_enteros_desde_cinta


def cinta_desde_tokens_enteros(enteros: list[int]) -> list[str]:
    """Construye una cinta a partir de una lista de enteros codificados."""
    cinta: list[str] = []
    for v in enteros:
        cinta.append(SEP)
        cinta.extend(list(str(v)))
    cinta.append(SEP)
    return cinta


tape_from_integer_tokens = cinta_desde_tokens_enteros


# ── Generacion de muestras de coseno ─────────────────────────────────────────

def muestras_coseno(n_muestras: int, omega: float = 1.0) -> list[float]:
    """
    Genera N muestras discretas de coseno: cos(w*k) para k=0..N-1.
    """
    return [math.cos(omega * k) for k in range(n_muestras)]


cosine_samples = muestras_coseno
