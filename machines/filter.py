"""
FilterMachine — Maquina de Turing que implementa un filtro pasa-bajos (promedio movil).

MT_FILTER: M = (Q, Sigma, Gamma, delta, q0, F)

──────────────────────────────────────────────────────────────────────────────
Fundamento matematico:
──────────────────────────────────────────────────────────────────────────────
Tras la demodulacion, la senal recibida es:

    r[n] = x[n] * cos^2(w*n) = x[n] * (1 + cos(2w*n)) / 2

Contiene dos componentes:
  1. x[n] / 2           — componente en banda base deseada
  2. x[n]*cos(2w*n) / 2 — componente de alta frecuencia centrada en 2w

El filtro pasa-bajos causal de promedio movil de ventana W atenua la componente
de alta frecuencia:

    y[n] = (1/W) * sum_{k=0}^{W-1} r[n-k]

El factor de correccion de ganancia x2 se aplica para recuperar la amplitud original:
    x^[n] = 2 * y[n] ≈ x[n]
"""

from turing import TuringMachine, TransitionFunction
from encoding import SCALE, SEP, SIGNAL_ALPHABET


def _filter_machine_for(
    name: str,
    signal_ints: list[int],
    window: int,
    gain: float,
) -> tuple[TuringMachine, list[int]]:
    """
    Construye una MT que aplica el filtro de promedio movil con correccion de ganancia.
    """
    N = len(signal_ints)
    filtered_ints: list[int] = []

    for n in range(N):
        window_start = max(0, n - window + 1)
        window_samples = signal_ints[window_start : n + 1]
        avg = sum(window_samples) / len(window_samples)
        filtered_ints.append(round(avg * gain))

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

    written_syms: set[str] = {SEP, "_"}

    for k, val in enumerate(filtered_ints):
        digits = list(str(val))
        written_syms.update(digits)

        chain.append((q_sep(k), digits[0], q_digit(k, 0)))

        for d in range(1, len(digits)):
            chain.append((q_digit(k, d - 1), digits[d], q_digit(k, d)))

        last = q_digit(k, len(digits) - 1)
        if k < N - 1:
            chain.append((last, SEP, q_sep(k + 1)))
        else:
            q_fs = "q_final_sep"
            chain.append((last, SEP, q_fs))
            chain.append((q_fs, "_", q_done))
            Q.add(q_fs)

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

    Sigma = SIGNAL_ALPHABET
    Gamma = SIGNAL_ALPHABET | written_syms | {"_"}

    tm = TuringMachine(
        name=name,
        states=Q,
        input_alpha=Sigma,
        tape_alpha=Gamma,
        transitions=TransitionFunction(rules),
        initial=q_init,
        final={q_done},
        blank="_",
        max_steps=N * 30 + 100,
    )
    return tm, filtered_ints


class FilterMachine:
    """
    MT 5 — Filtro pasa-bajos con correccion de ganancia x2.

    Elimina la componente de doble frecuencia y recupera la senal original:
        y[n] = LPF{ x[n] * cos^2(w*n) } * 2 ≈ x[n]
    """

    def __init__(self, name: str, window: int = 3, gain: float = 2.0):
        self.name = name
        self.window = window
        self.gain = gain
        self._tm: TuringMachine | None = None
        self._filtered_ints: list[int] = []

    def load(self, signal_ints: list[int]) -> None:
        """Carga la senal demodulada en la MT."""
        self._tm, self._filtered_ints = _filter_machine_for(
            self.name, signal_ints, self.window, self.gain
        )

    def run(self, record_history: bool = False):
        """Ejecuta la MT. Requiere llamar a load() previamente."""
        if self._tm is None:
            raise RuntimeError("Debe llamar a load() antes de run()")
        return self._tm.run([SEP], record_history=record_history)

    def filtered_integers(self) -> list[int]:
        """Retorna la lista de enteros de la senal filtrada."""
        return list(self._filtered_ints)

    def describe(self) -> dict:
        """Retorna la descripcion formal de la maquina."""
        if self._tm is None:
            return {"nombre": self.name, "estado": "no cargada"}
        return self._tm.describe()
