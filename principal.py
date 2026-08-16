"""
principal.py — Demostracion completa del sistema de comunicacion digital
              modelado rigurosamente mediante Maquinas de Turing.

Ejecucion:
    python principal.py
    python principal.py --sin-graficos
    python principal.py --ruido
    python principal.py --desajuste
"""

import sys
import os
import math
import argparse

# Forzar codificacion UTF-8 en Windows para evitar errores de consola
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from comunicacion import SistemaComunicacion
from maquinas import ConfiguracionCanal
from codificacion import ESCALA
from visualizacion import graficar_canalizacion, graficar_error


_CYAN   = "\033[96m"
_VERDE  = "\033[92m"
_AMARILLO = "\033[93m"
_ROJO    = "\033[91m"
_NEGRITA = "\033[1m"
_RESET  = "\033[0m"
_TENUE  = "\033[2m"


def _encabezado(texto: str) -> None:
    barra = "-" * 62
    print(f"\n{_NEGRITA}{_CYAN}{barra}{_RESET}")
    print(f"{_NEGRITA}{_CYAN}  {texto}{_RESET}")
    print(f"{_NEGRITA}{_CYAN}{barra}{_RESET}")


def _banner_etapa(nombre: str) -> None:
    print(f"\n{_NEGRITA}  v{_RESET}")
    print(f"  {_NEGRITA}[ {nombre} ]{_RESET}")


def _imprimir_resultado_mt(etapa) -> None:
    r = etapa.resultado_mt
    if r is None:
        print(f"  (componente fisico no-MT: {etapa.nombre})")
        return
    estado_str = f"{_VERDE}ACEPTADA{_RESET}" if r.aceptada else f"{_ROJO}DETENIDA{_RESET}"
    print(f"  Estado inicial : {_AMARILLO}{r.estado_inicial}{_RESET}")
    print(f"  Estado final   : {_AMARILLO}{r.estado_final}{_RESET}  ->  {estado_str}")
    print(f"  Pasos totales  : {r.pasos}")
    ints = etapa.enteros_senal
    vista_previa = ints[:4] + (["..."] if len(ints) > 8 else []) + (ints[-4:] if len(ints) > 8 else [])
    print(f"  Cinta (Q8)     : {vista_previa}")
    floats = etapa.senal_flotantes()
    floats_preview = [f"{v:.3f}" for v in floats[:4]]
    if len(floats) > 4:
        floats_preview.append("...")
    print(f"  Senal (float)  : [{', '.join(floats_preview)}]")


def _calcular_metricas(original: list[float], recuperada: list[float]) -> dict:
    errores = [abs(a - b) for a, b in zip(original, recuperada)]
    mae = sum(errores) / len(errores)
    mse = sum(e**2 for e in errores) / len(errores)
    return {"mae": mae, "mse": mse, "max_err": max(errores)}


def _describir_arquitectura_mt(resultado_sistema) -> None:
    _encabezado("ARQUITECTURA DE MAQUINAS DE TURING")
    print(
        f"\n  El sistema utiliza {_NEGRITA}5 Maquinas de Turing{_RESET} mas 1 modelo de canal fisico:\n"
        "\n"
        "  MT 2 -- MT_OSC_TX    Q = estados de escritura de cada digito de cos(w*k)\n"
        "  MT 1 -- MT_MULT_TX   Q = estados de escritura del producto modulado x*cos\n"
        "  CANAL  (no es MT)    modelo de medio fisico (ver maquinas/canal.py)\n"
        "  MT 4 -- MT_OSC_RX    Q = oscilador del receptor con frecuencia w_rx\n"
        "  MT 3 -- MT_MULT_RX   Q = multiplicador demodulador para y*cos\n"
        "  MT 5 -- MT_FILTER    Q = filtro pasa-bajos con factor de escala x2\n"
        "\n"
        "  Tupla formal de cada MT: M = (Q, Sigma, Gamma, delta, q0, F)\n"
        "    Sigma = { '0'..'9', '-', '|', '_' }\n"
        "    Gamma = Sigma union { digitos de valores calculados }\n"
        "    delta = funcion de transicion determinista: (q, s) -> (q', s', dir)\n"
        "    q0    = 'q_inicio'\n"
        "    F     = { 'q_fin' }\n"
    )
    for etapa in resultado_sistema.etapas:
        if etapa.resultado_mt is None:
            continue
        print(f"  {_NEGRITA}{etapa.nombre}{_RESET}: {etapa.resultado_mt.resumen()}")


def ejecutar_demostracion(
    mostrar_graficos: bool = True,
    modo_canal: str = "ideal",
    desajuste_omega: bool = False,
) -> None:
    _encabezado("SISTEMA DE COMUNICACION DIGITAL -- MAQUINAS DE TURING")
    print(
        "\n  Esquema academico de referencia:\n"
        "\n"
        "     TRANSMISOR (Tx)                     RECEPTOR (Rx)\n"
        "     ───────────────                     ─────────────\n"
        "  x[n] -> [MT_MULT_TX] -> x[n]cos(wn) -> CANAL -> [MT_MULT_RX] -> [MT_FILTER] -> x^[n]\n"
        "               ^                                         ^\n"
        "          [MT_OSC_TX]                             [MT_OSC_RX]\n"
        "          (MT 2, genera cos)                      (MT 4, genera cos)\n"
        "          (MT 1 = multiplicador Tx)               (MT 3 = mult Rx, MT 5 = filtro)\n"
    )

    N = 48
    OMEGA = 1.0
    VENTANA_FILTRO = 3

    senal_entrada = [0.8 * math.sin(2 * math.pi * 0.02 * k) for k in range(N)]
    omega_rx = 1.4 if desajuste_omega else OMEGA
    config_canal = ConfiguracionCanal(modo=modo_canal, desviacion_ruido=0.05, semilla=0)

    sistema = SistemaComunicacion(
        omega_tx=OMEGA,
        omega_rx=omega_rx,
        ventana_filtro=VENTANA_FILTRO,
        config_canal=config_canal,
    )

    print(f"  Senal de entrada: senoidal, N={N} muestras, f=0.02/muestra")
    print(f"  omega_tx={OMEGA}  omega_rx={omega_rx}  canal={modo_canal}  ventana_filtro={VENTANA_FILTRO}")
    vista_previa = [f"{v:.3f}" for v in senal_entrada[:6]] + ["..."]
    print(f"\n  {_NEGRITA}x[n] = {_RESET}[{', '.join(vista_previa)}]")

    _encabezado("EJECUCION PASO A PASO DE LA CANALIZACION")
    resultado = sistema.ejecutar(senal_entrada, registrar_historial=False)

    for etapa in resultado.etapas:
        _banner_etapa(etapa.nombre)
        print(f"  {etapa.descripcion}")
        _imprimir_resultado_mt(etapa)

    _encabezado("EVALUACION DEL RESULTADO FINAL")
    original = resultado.senal_entrada
    recuperada = resultado.senal_salida()
    metricas = _calcular_metricas(original, recuperada)

    print(f"\n  Senal original   x[n]  : [{', '.join(f'{v:.3f}' for v in original[:6])}, ...]")
    print(f"  Senal recuperada x^[n] : [{', '.join(f'{v:.3f}' for v in recuperada[:6])}, ...]")
    print()
    print(f"  {_NEGRITA}Metricas de fidelidad:{_RESET}")
    print(f"    MAE (Error Absoluto Medio)  = {_AMARILLO}{metricas['mae']:.5f}{_RESET}")
    print(f"    MSE (Error Cuadratico Medio)= {_AMARILLO}{metricas['mse']:.7f}{_RESET}")
    print(f"    Error Maximo                = {_AMARILLO}{metricas['max_err']:.5f}{_RESET}")

    calidad = "EXCELENTE" if metricas["mae"] < 0.08 else ("BUENA" if metricas["mae"] < 0.2 else "DEGRADADA")
    color = _VERDE if calidad in ("EXCELENTE", "BUENA") else _ROJO
    print(f"\n  Calidad de recuperacion: {color}{_NEGRITA}{calidad}{_RESET}")

    _describir_arquitectura_mt(resultado)

    if mostrar_graficos:
        print("\n  Generando graficos en pantalla...")
        try:
            graficar_canalizacion(resultado)
            graficar_error(original, recuperada)
        except Exception as exc:
            print(f"  No se pudo desplegar la ventana grafica: {exc}")
            print("  (Asegurese de tener un entorno grafico o ejecute con --sin-graficos / --no-plots)")

    print(f"\n{_NEGRITA}{_VERDE}  [OK] Demostracion completada exitosamente.{_RESET}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulador de Sistema de Comunicacion Digital basado en Maquinas de Turing"
    )
    parser.add_argument("--no-plots", "--sin-graficos", dest="no_plots", action="store_true",
                        help="Omitir visualizacion grafica con matplotlib")
    parser.add_argument("--noisy", "--ruido", dest="noisy", action="store_true",
                        help="Simular canal con ruido gaussiano aditivo")
    parser.add_argument("--mismatch", "--desajuste", dest="mismatch", action="store_true",
                        help="Simular desajuste de frecuencia entre transmisor y receptor")
    args = parser.parse_args()

    modo_canal = "noisy" if args.noisy else "ideal"

    ejecutar_demostracion(
        mostrar_graficos=not args.no_plots,
        modo_canal=modo_canal,
        desajuste_omega=args.mismatch,
    )


if __name__ == "__main__":
    main()
