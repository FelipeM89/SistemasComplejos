"""
Pruebas de integracion para la canalizacion completa de CommunicationSystem.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import unittest
from communication import CommunicationSystem
from machines import ChannelConfig
from encoding import SCALE


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
        sistema = CommunicationSystem(omega_tx=1.0, filter_window=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.run(senal)
        self.assertEqual(len(resultado.stages), 6)

    def test_nombres_de_todas_las_etapas_presentes(self):
        sistema = CommunicationSystem(omega_tx=1.0, filter_window=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.run(senal)
        nombres = {s.name for s in resultado.stages}
        self.assertIn("MT_OSC_TX", nombres)
        self.assertIn("MT_MULT_TX", nombres)
        self.assertIn("CANAL", nombres)
        self.assertIn("MT_OSC_RX", nombres)
        self.assertIn("MT_MULT_RX", nombres)
        self.assertIn("MT_FILTER", nombres)

    def test_longitud_salida_igual_a_entrada(self):
        N = 32
        sistema = CommunicationSystem(omega_tx=1.0, filter_window=3)
        senal = _senal_senoidal(N, freq=0.02)
        resultado = sistema.run(senal)
        self.assertEqual(len(resultado.output_signal()), N)

    def test_recuperacion_en_canal_ideal(self):
        """
        Con canal ideal, portadora omega=1.0 y ventana W=3, la componente
        de doble frecuencia 2w=2.0 se suprime eficazmente, logrando bajo MAE.
        """
        N = 48
        omega = 1.0
        sistema = CommunicationSystem(omega_tx=omega, filter_window=3)
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)
        resultado = sistema.run(senal)
        original = resultado.input_signal
        recuperada = resultado.output_signal()
        metricas = _calcular_metricas(original, recuperada)
        self.assertLess(metricas["mae"], 0.10, (
            f"MAE de recuperacion muy alto: {metricas['mae']:.4f}"
        ))

    def test_todas_las_maquinas_son_aceptadas(self):
        sistema = CommunicationSystem(omega_tx=1.0, filter_window=3)
        senal = _senal_senoidal(16, freq=0.02)
        resultado = sistema.run(senal)
        etapas_tm = [s for s in resultado.stages if s.tm_result is not None]
        for etapa in etapas_tm:
            self.assertTrue(
                etapa.tm_result.accepted,
                f"La maquina {etapa.name} no alcanzo estado de aceptacion",
            )

    def test_etapa_portadora_coincide_con_coseno(self):
        N = 8
        omega = 1.0
        sistema = CommunicationSystem(omega_tx=omega, filter_window=3)
        senal = [0.5] * N
        resultado = sistema.run(senal)

        portadora = resultado.stage("MT_OSC_TX").signal_ints
        esperada = [round(math.cos(omega * k) * SCALE) for k in range(N)]
        self.assertEqual(portadora, esperada)

    def test_etapa_modulacion(self):
        N = 8
        omega = 1.0
        sistema = CommunicationSystem(omega_tx=omega, filter_window=3)
        senal = [math.sin(0.1 * k) for k in range(N)]
        resultado = sistema.run(senal)

        signal_ints = [round(v * SCALE) for v in senal]
        carrier_ints = resultado.stage("MT_OSC_TX").signal_ints
        esperada = [round(a * b / SCALE) for a, b in zip(signal_ints, carrier_ints)]
        actual = resultado.stage("MT_MULT_TX").signal_ints
        self.assertEqual(actual, esperada)

    def test_senal_cuadrada_valores_acotados(self):
        N = 24
        sistema = CommunicationSystem(omega_tx=1.0, filter_window=3)
        senal = _senal_cuadrada(N)
        resultado = sistema.run(senal)
        recuperada = resultado.output_signal()
        self.assertEqual(len(recuperada), N)
        self.assertTrue(all(-2.0 <= val <= 2.0 for val in recuperada))

    def test_canal_con_ruido_incrementa_error(self):
        N = 48
        omega = 1.0
        sistema_ideal = CommunicationSystem(omega_tx=omega, filter_window=3)
        sistema_con_ruido = CommunicationSystem(
            omega_tx=omega,
            filter_window=3,
            channel_cfg=ChannelConfig(mode="noisy", noise_std=0.2, seed=42),
        )
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)

        res_ideal = sistema_ideal.run(senal)
        res_ruido = sistema_con_ruido.run(senal)

        mae_ideal = _calcular_metricas(res_ideal.input_signal, res_ideal.output_signal())["mae"]
        mae_ruido = _calcular_metricas(res_ruido.input_signal, res_ruido.output_signal())["mae"]

        self.assertGreater(mae_ruido, mae_ideal)

    def test_desajuste_de_frecuencia_degrada_recuperacion(self):
        N = 48
        senal = _senal_senoidal(N, freq=0.02, amp=0.8)

        ajustado = CommunicationSystem(omega_tx=1.0, omega_rx=1.0, filter_window=3)
        desajustado = CommunicationSystem(omega_tx=1.0, omega_rx=1.6, filter_window=3)

        res_ajustado = ajustado.run(senal)
        res_desajustado = desajustado.run(senal)

        mae_ajustado = _calcular_metricas(res_ajustado.input_signal, res_ajustado.output_signal())["mae"]
        mae_desajustado = _calcular_metricas(res_desajustado.input_signal, res_desajustado.output_signal())["mae"]

        self.assertGreater(mae_desajustado, mae_ajustado)


if __name__ == "__main__":
    unittest.main()
