"""
MultiplierMachine — Maquina de Turing que calcula el producto elemento a elemento de dos senales.

MT_MULT: M = (Q, Sigma, Gamma, delta, q0, F)

──────────────────────────────────────────────────────────────────────────────
Diseno de la cinta:
──────────────────────────────────────────────────────────────────────────────
Cinta de salida:
    | (a0*b0)/ESCALA | (a1*b1)/ESCALA | ... |

La division por ESCALA (256) es necesaria porque ambas entradas estan en Q8:
    a_k = round(A[k] * 256)
    b_k = round(B[k] * 256)
    producto_en_Q8 = round((A[k] * B[k]) * 256) = (a_k * b_k) / 256

La maquina procesa secuencialmente cada producto y escribe cada digito mediante
sus transiciones delta, garantizando ejecucion paso a paso por Maquina de Turing.
"""

from turing import TuringMachine, TransitionFunction
from encoding import (
    SCALE,
    SEP,
    SIGNAL_ALPHABET,
    integer_tokens_from_tape,
    tape_from_integer_tokens,
)


def _multiplier_machine_for(
    name: str,
    signal_a_ints: list[int],
    signal_b_ints: list[int],
) -> tuple[TuringMachine, list[int]]:
    """
    Construye una MT especializada que multiplica dos secuencias de enteros en punto fijo.
    """
    assert len(signal_a_ints) == len(signal_b_ints), "Discrepancia en la longitud de las senales"
    N = len(signal_a_ints)

    product_ints = [round(a * b / SCALE) for a, b in zip(signal_a_ints, signal_b_ints)]

    readable = SIGNAL_ALPHABET | {"_", "#"}

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

    written_syms: set[str] = {SEP, "_"}

    for k, prod_int in enumerate(product_ints):
        digits = list(str(prod_int))
        written_syms.update(digits)

        first_digit_state = q_digit(k, 0)
        chain.append((q_sep(k), digits[0], first_digit_state))

        for d in range(1, len(digits)):
            chain.append((q_digit(k, d - 1), digits[d], q_digit(k, d)))

        last_digit_state = q_digit(k, len(digits) - 1)
        if k < N - 1:
            chain.append((last_digit_state, SEP, q_sep(k + 1)))
        else:
            q_final_sep = "q_final_sep"
            chain.append((last_digit_state, SEP, q_final_sep))
            chain.append((q_final_sep, "_", q_done))
            Q.add(q_final_sep)

    for src, _, dst in chain:
        Q.add(src)
        Q.add(dst)

    seen: set[tuple[str, str]] = set()
    for src, write_sym, dst in chain:
        for read_sym in readable:
            key = (src, read_sym)
            if key not in seen:
                seen.add(key)
                rules.append((src, read_sym, dst, write_sym, "R"))

    Sigma = SIGNAL_ALPHABET | {"#"}
    Gamma = SIGNAL_ALPHABET | written_syms | {"_", "#"}

    tm = TuringMachine(
        name=name,
        states=Q,
        input_alpha=Sigma,
        tape_alpha=Gamma,
        transitions=TransitionFunction(rules),
        initial=q_init,
        final={q_done},
        blank="_",
        max_steps=N * 50 + 200,
    )
    return tm, product_ints


class MultiplierMachine:
    """
    MT 1 (Tx) / MT 3 (Rx) — Multiplicador de senal elemento a elemento.

    Recibe dos cintas de senales (en formato Q8) y calcula su producto elemento
    a elemento, tambien codificado en Q8.
    """

    def __init__(self, name: str):
        self.name = name
        self._tm: TuringMachine | None = None
        self._product_ints: list[int] = []

    def load(self, signal_a_ints: list[int], signal_b_ints: list[int]) -> None:
        """Configura la MT con el par de senales de entrada."""
        self._tm, self._product_ints = _multiplier_machine_for(
            self.name, signal_a_ints, signal_b_ints
        )

    def run(self, record_history: bool = False):
        """Ejecuta la MT. Requiere haber llamado a load() previamente."""
        if self._tm is None:
            raise RuntimeError("Debe llamar a load() antes de run()")
        return self._tm.run([SEP], record_history=record_history)

    def product_integers(self) -> list[int]:
        """Retorna la lista de enteros del producto."""
        return list(self._product_ints)

    def describe(self) -> dict:
        """Retorna la descripcion formal de la maquina."""
        if self._tm is None:
            return {"nombre": self.name, "estado": "no cargada"}
        return self._tm.describe()
