"""
Pruebas para el modulo de codificacion y las maquinas de senal (Oscilador, Multiplicador, Filtro).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import unittest
from encoding import (
    encode_signal,
    decode_signal,
    integer_tokens_from_tape,
    tape_from_integer_tokens,
    cosine_samples,
    SCALE,
    SEP,
)
from machines import OscillatorMachine, MultiplierMachine, FilterMachine


# ── Codificacion ─────────────────────────────────────────────────────────────

class TestCodificacion(unittest.TestCase):
    def test_ida_y_vuelta_simple(self):
        original = [0.5, -0.5, 1.0, -1.0, 0.0]
        tape = encode_signal(original)
        recovered = decode_signal(tape)
        for orig, rec in zip(original, recovered):
            self.assertAlmostEqual(orig, rec, delta=1 / SCALE + 1e-9)

    def test_codificar_muestra_positiva(self):
        tape = encode_signal([1.0])
        recovered = decode_signal(tape)
        self.assertAlmostEqual(recovered[0], 1.0, delta=1 / SCALE + 1e-9)

    def test_codificar_muestra_negativa(self):
        tape = encode_signal([-0.75])
        recovered = decode_signal(tape)
        self.assertAlmostEqual(recovered[0], -0.75, delta=1 / SCALE + 1e-9)

    def test_tokens_enteros_ida_y_vuelta(self):
        integers = [100, -200, 0, 128, -128]
        tape = tape_from_integer_tokens(integers)
        recovered = integer_tokens_from_tape(tape)
        self.assertEqual(recovered, integers)

    def test_muestras_coseno_frecuencia_cero(self):
        samples = cosine_samples(4, omega=0.0)
        self.assertTrue(all(abs(s - 1.0) < 1e-12 for s in samples))

    def test_muestras_coseno_pi_medios(self):
        omega = math.pi / 2
        samples = cosine_samples(4, omega=omega)
        expected = [math.cos(omega * k) for k in range(4)]
        for s, e in zip(samples, expected):
            self.assertAlmostEqual(s, e, places=10)


# ── Oscilador ────────────────────────────────────────────────────────────────

class TestMaquinaOscilador(unittest.TestCase):
    def test_longitud_de_salida(self):
        osc = OscillatorMachine("test_osc", n_samples=8, omega=0.5)
        result = osc.run()
        ints = integer_tokens_from_tape(result.tape_content)
        self.assertEqual(len(ints), 8)

    def test_salida_coincide_con_coseno_teorico(self):
        omega = 0.5
        N = 6
        osc = OscillatorMachine("test_osc", n_samples=N, omega=omega)
        result = osc.run()
        ints = integer_tokens_from_tape(result.tape_content)
        expected = [round(math.cos(omega * k) * SCALE) for k in range(N)]
        self.assertEqual(ints, expected)

    def test_maquina_se_detiene_y_acepta(self):
        osc = OscillatorMachine("test_osc", n_samples=4, omega=1.0)
        result = osc.run()
        self.assertTrue(result.accepted)

    def test_componentes_formales_en_descripcion(self):
        osc = OscillatorMachine("test_osc", n_samples=4, omega=0.5)
        desc = osc.describe()
        self.assertIn("q0", desc)
        self.assertIn("F", desc)
        self.assertIn("Q", desc)
        self.assertIn("Sigma", desc)
        self.assertIn("Gamma", desc)

    def test_frecuencias_distintas_producen_salidas_distintas(self):
        osc1 = OscillatorMachine("osc1", 8, omega=0.3)
        osc2 = OscillatorMachine("osc2", 8, omega=0.7)
        r1 = integer_tokens_from_tape(osc1.run().tape_content)
        r2 = integer_tokens_from_tape(osc2.run().tape_content)
        self.assertNotEqual(r1, r2)


# ── Multiplicador ────────────────────────────────────────────────────────────

class TestMaquinaMultiplicador(unittest.TestCase):
    def test_multiplicacion_por_uno_es_identidad(self):
        N = 6
        signal_ints = [round(v * SCALE) for v in [0.5, -0.5, 0.25, -0.25, 0.0, 1.0]]
        ones_ints = [SCALE] * N

        mult = MultiplierMachine("test_mult")
        mult.load(signal_ints, ones_ints)
        result = mult.run()
        out_ints = integer_tokens_from_tape(result.tape_content)

        expected = [round(a * b / SCALE) for a, b in zip(signal_ints, ones_ints)]
        self.assertEqual(out_ints, expected)

    def test_multiplicacion_por_cero_da_cero(self):
        signal_ints = [SCALE, -SCALE, 128]
        zero_ints = [0, 0, 0]
        mult = MultiplierMachine("test_mult")
        mult.load(signal_ints, zero_ints)
        result = mult.run()
        out_ints = integer_tokens_from_tape(result.tape_content)
        self.assertTrue(all(v == 0 for v in out_ints))

    def test_maquina_se_detiene_y_acepta(self):
        mult = MultiplierMachine("test_mult")
        mult.load([SCALE, SCALE], [SCALE, SCALE])
        result = mult.run()
        self.assertTrue(result.accepted)

    def test_longitud_salida_coincide_con_entrada(self):
        N = 10
        signal_ints = [round(math.cos(k * 0.3) * SCALE) for k in range(N)]
        carrier_ints = [round(math.cos(k * 0.3) * SCALE) for k in range(N)]
        mult = MultiplierMachine("test_mult")
        mult.load(signal_ints, carrier_ints)
        result = mult.run()
        out_ints = integer_tokens_from_tape(result.tape_content)
        self.assertEqual(len(out_ints), N)

    def test_requiere_load_antes_de_run(self):
        mult = MultiplierMachine("test_mult")
        with self.assertRaises(RuntimeError):
            mult.run()


# ── Filtro ───────────────────────────────────────────────────────────────────

class TestMaquinaFiltro(unittest.TestCase):
    def test_senal_constante_con_ganancia_unitaria(self):
        constant = [SCALE] * 10
        filt = FilterMachine("test_filt", window=4, gain=1.0)
        filt.load(constant)
        result = filt.run()
        out_ints = integer_tokens_from_tape(result.tape_content)
        self.assertTrue(all(abs(v - SCALE) <= 1 for v in out_ints))

    def test_longitud_salida_coincide_con_entrada(self):
        N = 8
        signal_ints = [round(math.sin(k * 0.5) * SCALE) for k in range(N)]
        filt = FilterMachine("test_filt", window=4, gain=2.0)
        filt.load(signal_ints)
        result = filt.run()
        out_ints = integer_tokens_from_tape(result.tape_content)
        self.assertEqual(len(out_ints), N)

    def test_maquina_se_detiene_y_acepta(self):
        filt = FilterMachine("test_filt", window=4, gain=2.0)
        filt.load([SCALE, SCALE, SCALE, SCALE])
        result = filt.run()
        self.assertTrue(result.accepted)

    def test_requiere_load_antes_de_run(self):
        filt = FilterMachine("test_filt")
        with self.assertRaises(RuntimeError):
            filt.run()

    def test_atenuacion_alta_frecuencia(self):
        N = 20
        nyquist = [SCALE * ((-1) ** k) for k in range(N)]
        filt = FilterMachine("test_filt", window=4, gain=1.0)
        filt.load(nyquist)
        result = filt.run()
        out_ints = integer_tokens_from_tape(result.tape_content)
        for v in out_ints[4:]:
            self.assertLess(abs(v), SCALE * 0.15)


if __name__ == "__main__":
    unittest.main()
