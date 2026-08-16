"""
OscillatorMachine — Maquina de Turing que genera una portadora discreta en su cinta.

MT_OSC: M = (Q, Sigma, Gamma, delta, q0, F)

Justificacion teorica:
──────────────────────
Una Maquina de Turing con un programa fijo (delta) que genera y escribe una
secuencia predeterminada modela formalmente un *generador* computacional.
La funcion calculada mapea la cinta inicial a la secuencia discreta de coseno
cos(w*k) para k=0..N-1 codificada en formato Q8.

La tabla de transiciones se construye deterministamente a partir de N y w:
  - Dispone de una cinta que se escribe secuencialmente celda por celda.
  - El cabezal se desplaza hacia la derecha.
  - El conjunto de estados crece linealmente con N x (digitos_por_muestra), siendo FINITO.
  - La computacion termina en un estado de aceptacion garantizado.

Diseno de la cinta de salida:
    | v0 | v1 | ... | v_{N-1} |
donde cada v_k es la cadena de enteros en Q8 de cos(w*k).
"""

from turing import TuringMachine, TransitionFunction
from encoding import SCALE, SEP, SIGNAL_ALPHABET, cosine_samples


def _oscillator_machine(name: str, n_samples: int, omega: float) -> TuringMachine:
    """
    Construye la Maquina de Turing para el oscilador.

    Convencion de nombres de estados:
        q_init              — estado inicial
        q_sep_{k}           — a punto de escribir el SEP antes de la muestra k
        q_digit_{k}_{d}     — a punto de escribir el digito d de la muestra k
        q_done              — estado final de aceptacion
    """
    cos_ints = [round(v * SCALE) for v in cosine_samples(n_samples, omega)]

    readable = SIGNAL_ALPHABET | {"_"}

    Q: set[str] = set()
    rules: list[tuple] = []

    q_init = "q_init"
    q_done = "q_done"
    Q.add(q_init)
    Q.add(q_done)

    def q_sep(k: int) -> str:
        return f"q_sep_{k}"

    def q_digit(k: int, d: int) -> str:
        return f"q_digit_{k}_{d}"

    chain: list[tuple[str, str, str]] = []
    chain.append((q_init, SEP, q_sep(0)))

    for k, cos_int in enumerate(cos_ints):
        digits = list(str(cos_int))

        first_digit_state = q_digit(k, 0)
        chain.append((q_sep(k), digits[0], first_digit_state))

        for d in range(1, len(digits)):
            prev = q_digit(k, d - 1)
            curr = q_digit(k, d)
            chain.append((prev, digits[d], curr))

        last_digit_state = q_digit(k, len(digits) - 1)
        if k < n_samples - 1:
            chain.append((last_digit_state, SEP, q_sep(k + 1)))
        else:
            q_final_sep = "q_final_sep"
            chain.append((last_digit_state, SEP, q_final_sep))
            chain.append((q_final_sep, "_", q_done))
            Q.add(q_final_sep)

    for src, _, dst in chain:
        Q.add(src)
        Q.add(dst)

    written_syms: set[str] = set()
    for src, write_sym, dst in chain:
        written_syms.add(write_sym)
        for read_sym in readable:
            rules.append((src, read_sym, dst, write_sym, "R"))

    seen: set[tuple[str, str]] = set()
    unique_rules: list[tuple] = []
    for r in rules:
        key = (r[0], r[1])
        if key not in seen:
            seen.add(key)
            unique_rules.append(r)

    Sigma = SIGNAL_ALPHABET
    Gamma = SIGNAL_ALPHABET | written_syms | {"_"}

    return TuringMachine(
        name=name,
        states=Q,
        input_alpha=Sigma,
        tape_alpha=Gamma,
        transitions=TransitionFunction(unique_rules),
        initial=q_init,
        final={q_done},
        blank="_",
        max_steps=n_samples * 30 + 100,
    )


class OscillatorMachine:
    """
    MT 2 (Tx) / MT 4 (Rx) — Generador de portadora discreta de coseno.

    Implementa una Maquina de Turing M=(Q, Sigma, Gamma, delta, q0, F) que escribe:
        cos(w*0), cos(w*1), ..., cos(w*(N-1))
    como enteros en punto fijo Q8 en su cinta.
    """

    def __init__(self, name: str, n_samples: int, omega: float = 1.0):
        self.name = name
        self.n_samples = n_samples
        self.omega = omega
        self._cos_ints = [round(v * SCALE) for v in cosine_samples(n_samples, omega)]
        self._tm = _oscillator_machine(name, n_samples, omega)

    def run(self, record_history: bool = False):
        """Ejecuta la MT sobre la cinta. Retorna ExecutionResult."""
        return self._tm.run([SEP], record_history=record_history)

    def carrier_integers(self) -> list[int]:
        """Retorna la lista de enteros Q8 de la portadora."""
        return list(self._cos_ints)

    def describe(self) -> dict:
        """Retorna la descripcion formal de la maquina."""
        return self._tm.describe()
