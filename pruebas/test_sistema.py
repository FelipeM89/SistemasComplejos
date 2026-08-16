"""
Pruebas de integracion para la canalizacion completa de SistemaComunicacion.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import unittest
from comunicacion import SistemaComunicacion
from maquinas import ConfiguracionCanal
from codificacion import ESCALA


def _senal_senoidal(N: int, freq: float = 0.02, amp: float = 0.8) -> list[float]:
    return [amp * math.sin(2 * math.pi * freq * k) for k in range(N)]


def _senal_cuadrada(N: int) -> list[float]:
    return [1.0 if k % 4 < 2 else -1.0 for k in range(N)]


def _calcular_metricas(original: list[float], recuperada: list[float]) -> dict:
    errores = [abs(a - b) for a, b in zip(original, recuperada)]
    mae = sum(errores) / len(errores)
    mse = sum(e**2 for e in errores) / len(errores)
    max_err = max(errores)
    return {"mae": mae, "mse": mse, "max_err": max_err}


class TestSistemaComunicacion(unittest.TestCase):
    def test_pipeline_produce_seis_etapas(self):
        sistema = SistemaComunicacion(omega_tx=1.0, ventana_filtro=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.ejecutar(senal)
        self.assertEqual(len(resultado.etapas), 6)

    def test_nombres_de_todas_las_etapas_presentes(self):
        sistema = SistemaComunicacion(omega_tx=1.0, ventana_filtro=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.ejecutar(senal)
        nombres = {e.nombre for e in resultado.etapas}
        self.assertIn("MT_OSC_TX", nombres)
        self.assertIn("MT_MULT_TX", nombres)
        self.assertIn("CANAL", nombres)
        self.assertIn("MT_OSC_RX", nombres)
        self.assertIn("MT_MULT_RX", nombres)
        self.assertIn("MT_FILTER", nombres)

    def test_longitud_salida_igual_a_entrada(self):
        N = 32
        sistema = SistemaComunicacion(omega_tx=1.0, ventana_filtro=3)
        senal = _senal_senoidal(N, freq=0.02)
        resultado = sistema.ejecutar(senal)
        self.assertEqual(len(resultado.senal_salida()), N)

    def test_recuperacion_en_canal_ideal(self):
        N = 48
        omega = 1.0
        sistema = SistemaComunicacion(omega_tx=omega, ventana_filtro=3)
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)
        resultado = sistema.ejecutar(senal)
        original = resultado.senal_entrada
        recuperada = resultado.senal_salida()
        metricas = _calcular_metricas(original, recuperada)
        self.assertLess(metricas["mae"], 0.10, (
            f"MAE de recuperacion muy alto: {metricas['mae']:.4f}"
        ))

    def test_todas_las_maquinas_son_aceptadas(self):
        sistema = SistemaComunicacion(omega_tx=1.0, ventana_filtro=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.ejecutar(senal)
        etapas_tm = [e for e in resultado.etapas if e.resultado_mt is not None]
        for etapa in etapas_tm:
            self.assertTrue(
                etapa.resultado_mt.aceptada,
                f"La maquina {etapa.nombre} no alcanzo estado de aceptacion",
            )

    def test_etapa_portadora_coincide_con_coseno(self):
        N = 8
        omega = 1.0
        sistema = SistemaComunicacion(omega_tx=omega, ventana_filtro=3)
        senal = [0.5] * N
        resultado = sistema.ejecutar(senal)

        portadora = resultado.etapa("MT_OSC_TX").enteros_senal
        esperada = [round(math.cos(omega * k) * ESCALA) for k in range(N)]
        self.assertEqual(portadora, esperada)

    def test_etapa_modulacion(self):
        N = 8
        omega = 1.0
        sistema = SistemaComunicacion(omega_tx=omega, ventana_filtro=3)
        senal = [math.sin(0.1 * k) for k in range(N)]
        resultado = sistema.ejecutar(senal)

        enteros_senal = [round(v * ESCALA) for v in senal]
        enteros_portadora = resultado.etapa("MT_OSC_TX").enteros_senal
        esperada = [round(a * b / ESCALA) for a, b in zip(enteros_senal, enteros_portadora)]
        actual = resultado.etapa("MT_MULT_TX").enteros_senal
        self.assertEqual(actual, esperada)

    def test_senal_cuadrada_valores_acotados(self):
        N = 24
        sistema = SistemaComunicacion(omega_tx=1.0, ventana_filtro=3)
        senal = _senal_cuadrada(N)
        resultado = sistema.ejecutar(senal)
        recuperada = resultado.senal_salida()
        self.assertEqual(len(recuperada), N)
        self.assertTrue(all(-2.0 <= val <= 2.0 for val in recuperada))

    def test_canal_con_ruido_incrementa_error(self):
        N = 48
        omega = 1.0
        sistema_ideal = SistemaComunicacion(omega_tx=omega, ventana_filtro=3)
        sistema_con_ruido = SistemaComunicacion(
            omega_tx=omega,
            ventana_filtro=3,
            config_canal=ConfiguracionCanal(modo="noisy", desviacion_ruido=0.2, semilla=42),
        )
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)

        res_ideal = sistema_ideal.ejecutar(senal)
        res_ruido = sistema_con_ruido.ejecutar(senal)

        mae_ideal = _calcular_metricas(res_ideal.senal_entrada, res_ideal.senal_salida())["mae"]
        mae_ruido = _calcular_metricas(res_ruido.senal_entrada, res_ruido.senal_salida())["mae"]

        self.assertGreater(mae_ruido, mae_ideal)

    def test_desajuste_de_frecuencia_degrada_recuperacion(self):
        N = 48
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)

        ajustado = SistemaComunicacion(omega_tx=1.0, omega_rx=1.0, ventana_filtro=3)
        desajustado = SistemaComunicacion(omega_tx=1.0, omega_rx=1.6, ventana_filtro=3)

        res_ajustado = ajustado.ejecutar(senal)
        res_desajustado = desajustado.ejecutar(senal)

        mae_ajustado = _calcular_metricas(res_ajustado.senal_entrada, res_ajustado.senal_salida())["mae"]
        mae_desajustado = _calcular_metricas(res_desajustado.senal_entrada, res_desajustado.senal_salida())["mae"]

        self.assertGreater(mae_desajustado, mae_ajustado)


if __name__ == "__main__":
    unittest.main()
