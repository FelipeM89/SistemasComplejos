"""
Visualizacion — graficos para la canalizacion del sistema de comunicacion.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from communication import SystemResult
from encoding import SCALE


_ETIQUETAS_ETAPAS = {
    "MT_OSC_TX":  "Portadora TX: cos(w*n)",
    "MT_OSC_RX":  "Portadora RX: cos(w*n)",
    "MT_MULT_TX": "Senal modulada: x[n] * cos(w*n)",
    "CANAL":      "Despues del canal: y[n]",
    "MT_MULT_RX": "Demodulada: y[n] * cos(w*n)",
    "MT_FILTER":  "Recuperada: x^[n] (filtro + ganancia x2)",
}

_COLORES = {
    "input":      "#4FC3F7",
    "MT_OSC_TX":  "#81C784",
    "MT_MULT_TX": "#FFB74D",
    "CANAL":      "#E57373",
    "MT_OSC_RX":  "#9575CD",
    "MT_MULT_RX": "#F06292",
    "MT_FILTER":  "#4DB6AC",
    "output":     "#FFF176",
}


def plot_pipeline(system_result: SystemResult, save_path: str | None = None) -> None:
    """
    Genera una cuadricula de subgraficos mostrando cada etapa de la canalizacion.
    """
    input_sig = system_result.input_signal
    N = len(input_sig)
    n = list(range(N))

    stages_to_plot = [
        ("Senal original x[n]", input_sig, _COLORES["input"]),
        ("Portadora TX cos(w*n)",
         system_result.stage("MT_OSC_TX").signal_floats(), _COLORES["MT_OSC_TX"]),
        ("Modulada x[n] * cos(w*n)",
         system_result.stage("MT_MULT_TX").signal_floats(), _COLORES["MT_MULT_TX"]),
        ("Canal y[n]",
         system_result.stage("CANAL").signal_floats(), _COLORES["CANAL"]),
        ("Portadora RX cos(w*n)",
         system_result.stage("MT_OSC_RX").signal_floats(), _COLORES["MT_OSC_RX"]),
        ("Demodulada y[n] * cos(w*n)",
         system_result.stage("MT_MULT_RX").signal_floats(), _COLORES["MT_MULT_RX"]),
        ("Filtrada (LPF x 2) x^[n]",
         system_result.stage("MT_FILTER").signal_floats(), _COLORES["MT_FILTER"]),
        ("Comparacion: x[n] vs x^[n]", None, None),
    ]

    fig = plt.figure(figsize=(16, 14), facecolor="#1a1a2e")
    fig.suptitle(
        "Sistema de Comunicacion Digital — Modulacion por Maquinas de Turing",
        color="white",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )
    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.55, wspace=0.35)

    for idx, (label, signal, color) in enumerate(stages_to_plot):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        ax.set_facecolor("#16213e")
        for spine in ax.spines.values():
            spine.set_color("#334")

        if label.startswith("Comparacion"):
            recovered = system_result.stage("MT_FILTER").signal_floats()
            ax.plot(n, input_sig, color=_COLORES["input"], linewidth=1.8,
                    label="Original x[n]", marker="o", markersize=3)
            ax.plot(n, recovered, color=_COLORES["MT_FILTER"], linewidth=1.8,
                    label="Recuperada x^[n]", linestyle="--", marker="s", markersize=3)
            ax.legend(facecolor="#1a1a2e", edgecolor="#334", labelcolor="white",
                      fontsize=9)
        else:
            ax.plot(n, signal, color=color, linewidth=1.8, marker="o", markersize=3)
            ax.axhline(0, color="#445", linewidth=0.8, linestyle="--")

        ax.set_title(label, color="white", fontsize=9, pad=4)
        ax.tick_params(colors="#aaa", labelsize=8)
        ax.set_xlabel("Muestra n", color="#aaa", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"  Grafico guardado en: {save_path}")
    else:
        plt.show()

    plt.close(fig)


def plot_error(
    original: list[float],
    recovered: list[float],
    save_path: str | None = None,
) -> None:
    """Grafica el error absoluto entre la senal original y la recuperada."""
    error = [abs(a - b) for a, b in zip(original, recovered)]
    n = list(range(len(original)))

    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.plot(n, error, color="#EF5350", linewidth=1.5, marker="o", markersize=4)
    ax.axhline(0, color="#445", linewidth=0.8, linestyle="--")
    ax.set_title("Error absoluto: |x[n] − x^[n]|", color="white", fontsize=11)
    ax.tick_params(colors="#aaa")
    ax.set_xlabel("Muestra n", color="#aaa")
    ax.set_ylabel("|Error|", color="#aaa")
    for spine in ax.spines.values():
        spine.set_color("#334")

    mae = sum(error) / len(error)
    mse = sum(e**2 for e in error) / len(error)
    max_err = max(error)
    ax.text(
        0.02, 0.92,
        f"MAE={mae:.4f}  MSE={mse:.6f}  Max={max_err:.4f}",
        transform=ax.transAxes,
        color="#FFF176",
        fontsize=9,
        va="top",
    )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=120, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  Grafico de error guardado en: {save_path}")
    else:
        plt.show()
    plt.close(fig)
