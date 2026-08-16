"""
Codificacion y decodificacion de senales para cintas de Maquinas de Turing.

── Diseno de la representacion ────────────────────────────────────────────────

Las senales continuas x(t) y cos(w*t) se discretizan en N muestras. Cada valor
de muestra (un numero real en un rango acotado) se mapea a un entero de punto
fijo en formato Q:

    codificado = round(valor * ESCALA)        (entero)

ESCALA = 2**PRECISION  (por defecto PRECISION=8 -> ESCALA=256)

Esto otorga una resolucion de 1/256 ≈ 0.0039. Para |x| <= 1 los enteros
codificados se encuentran en el rango [-256, 256].

Diseno de la cinta para una senal de N muestras:
─────────────────────────────────────────────────
    SEP  v0  SEP  v1  SEP  ...  SEP  v_{N-1}  SEP

donde:
  SEP = "|"   — separador de muestras
  v_k         — cada muestra codificada como una secuencia de caracteres digito
                con un signo "-" inicial opcional para valores negativos.

Ejemplo (4 muestras, ESCALA=4):
    senal      = [1.0, 0.5, -0.5, -1.0]
    codificado = [4, 2, -2, -4]
    cinta      = ["|","4","|","2","|","-","2","|","-","4","|"]

Las maquinas de Turing leen y escriben simbolos del alfabeto:
    Gamma_senal = {"0","1","2","3","4","5","6","7","8","9","-","|","_"}

Justificacion teorica:
──────────────────────
• Una maquina de Turing opera sobre un alfabeto finito. Codificar enteros como
  cadenas de digitos decimales es el enfoque estandar de la teoria de la computacion.
• El separador "|" permite a la maquina delimitar las muestras sin requerir
  un tamano fijo de celda.
• Los numeros negativos usan el prefijo "-", permitiendo operaciones con signo.
• ESCALA es una constante compartida por todas las maquinas para garantizar la
  consistencia composicional de todo el sistema.
"""

import math

PRECISION: int = 8               # bits de precision fraccionaria
ESCALA: int = 2 ** PRECISION     # 256
SCALE = ESCALA                   # Alias de compatibilidad

SEP: str = "|"
DIGITOS: set[str] = set("0123456789")
DIGITS = DIGITOS
SIGNO: str = "-"
SIGN = SIGNO
BLANCO: str = "_"
BLANK = BLANCO

# Alfabeto completo de cinta para maquinas de senal
ALFABETO_SENAL: set[str] = DIGITOS | {SIGNO, SEP, BLANCO}
SIGNAL_ALPHABET = ALFABETO_SENAL


# ── Codificacion ─────────────────────────────────────────────────────────────

def encode_sample(value: float) -> list[str]:
    """Float -> lista de simbolos de cinta que representan una muestra."""
    integer = round(value * ESCALA)
    return list(str(integer))


def encode_signal(samples: list[float]) -> list[str]:
    """
    Lista de flotantes -> lista plana de simbolos para la cinta.

    Formato: SEP v0 SEP v1 SEP ... SEP v_{n-1} SEP
    """
    tape: list[str] = []
    for s in samples:
        tape.append(SEP)
        tape.extend(encode_sample(s))
    tape.append(SEP)
    return tape


# ── Decodificacion ───────────────────────────────────────────────────────────

def _parse_tape_tokens(tape_symbols: list[str]) -> list[str]:
    """Divide el contenido de la cinta por SEP y descarta tokens vacios o blancos."""
    content = "".join(tape_symbols)
    return [t for t in content.split(SEP) if t and t != BLANCO]


def decode_sample(token: str) -> float:
    """Token de cinta (cadena de digitos) -> valor float."""
    return int(token) / ESCALA


def decode_signal(tape_symbols: list[str]) -> list[float]:
    """Lista plana de simbolos de cinta -> lista de flotantes decodificados."""
    return [decode_sample(t) for t in _parse_tape_tokens(tape_symbols)]


# ── Utilidades para las Maquinas de Turing ───────────────────────────────────

def integer_tokens_from_tape(tape_symbols: list[str]) -> list[int]:
    """Extrae los valores enteros codificados (sin dividir por ESCALA)."""
    return [int(t) for t in _parse_tape_tokens(tape_symbols)]


def tape_from_integer_tokens(integers: list[int]) -> list[str]:
    """Construye una cinta a partir de una lista de enteros codificados."""
    tape: list[str] = []
    for v in integers:
        tape.append(SEP)
        tape.extend(list(str(v)))
    tape.append(SEP)
    return tape


# ── Generacion de muestras de coseno (utilizado por MT_OSC) ───────────────────

def cosine_samples(n_samples: int, omega: float = 1.0) -> list[float]:
    """
    Genera N muestras discretas de coseno: cos(w*k) para k=0..N-1.

    omega es la frecuencia angular en radianes por muestra.
    """
    return [math.cos(omega * k) for k in range(n_samples)]
