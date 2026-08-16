"""
Pruebas para el modulo de codificacion y las maquinas de senal (Oscilador, Multiplicador, Filtro).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import unittest
from codificacion import (
    codificar_senal,
    decodificar_senal,
    tokens_enteros_desde_cinta,
    cinta_desde_tokens_enteros,
    muestras_coseno,
    ESCALA,
    SEP,
)
from maquinas import MaquinaOscilador, MaquinaMultiplicador, MaquinaFiltro


class TestCodificacion(unittest.TestCase):
    def test_ida_y_vuelta_simple(self):
        original = [0.5, -0.5, 1.0, -1.0, 0.0]
        cinta = codificar_senal(original)
        recuperada = decodificar_senal(cinta)
        for orig, rec in zip(original, recuperada):
            self.assertAlmostEqual(orig, rec, delta=1 / ESCALA + 1e-9)

    def test_codificar_muestra_positiva(self):
        cinta = codificar_senal([1.0])
        recuperada = decodificar_senal(cinta)
        self.assertAlmostEqual(recuperada[0], 1.0, delta=1 / ESCALA + 1e-9)

    def test_codificar_muestra_negativa(self):
        cinta = codificar_senal([-0.75])
        recuperada = decodificar_senal(cinta)
        self.assertAlmostEqual(recuperada[0], -0.75, delta=1 / ESCALA + 1e-9)

    def test_tokens_enteros_ida_y_vuelta(self):
        enteros = [100, -200, 0, 128, -128]
        cinta = cinta_desde_tokens_enteros(enteros)
        recuperados = tokens_enteros_desde_cinta(cinta)
        self.assertEqual(recuperados, enteros)

    def test_muestras_coseno_frecuencia_cero(self):
        muestras = muestras_coseno(4, omega=0.0)
        self.assertTrue(all(abs(s - 1.0) < 1e-12 for s in muestras))

    def test_muestras_coseno_pi_medios(self):
        omega = math.pi / 2
        muestras = muestras_coseno(4, omega=omega)
        esperadas = [math.cos(omega * k) for k in range(4)]
        for s, e in zip(muestras, esperadas):
            self.assertAlmostEqual(s, e, places=10)


class TestMaquinaOscilador(unittest.TestCase):
    def test_longitud_de_salida(self):
        osc = MaquinaOscilador("test_osc", n_muestras=8, omega=0.5)
        resultado = osc.ejecutar()
        enteros = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertEqual(len(enteros), 8)

    def test_salida_coincide_con_coseno_teorico(self):
        omega = 0.5
        N = 6
        osc = MaquinaOscilador("test_osc", n_muestras=N, omega=omega)
        resultado = osc.ejecutar()
        enteros = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        esperados = [round(math.cos(omega * k) * ESCALA) for k in range(N)]
        self.assertEqual(enteros, esperados)

    def test_maquina_se_detiene_y_acepta(self):
        osc = MaquinaOscilador("test_osc", n_muestras=4, omega=1.0)
        resultado = osc.ejecutar()
        self.assertTrue(resultado.aceptada)

    def test_componentes_formales_en_descripcion(self):
        osc = MaquinaOscilador("test_osc", n_muestras=4, omega=0.5)
        desc = osc.describir()
        self.assertIn("q0", desc)
        self.assertIn("F", desc)
        self.assertIn("Q", desc)
        self.assertIn("Sigma", desc)
        self.assertIn("Gamma", desc)

    def test_frecuencias_distintas_producen_salidas_distintas(self):
        osc1 = MaquinaOscilador("osc1", 8, omega=0.3)
        osc2 = MaquinaOscilador("osc2", 8, omega=0.7)
        r1 = tokens_enteros_desde_cinta(osc1.ejecutar().contenido_cinta)
        r2 = tokens_enteros_desde_cinta(osc2.ejecutar().contenido_cinta)
        self.assertNotEqual(r1, r2)

    def test_ejecucion_paso_a_paso_en_cinta(self):
        osc = MaquinaOscilador("test_osc", n_muestras=4, omega=1.0)
        resultado = osc.ejecutar(registrar_historial=True)
        self.assertGreater(resultado.pasos, 0)
        self.assertGreater(len(resultado.historial), 0)


class TestMaquinaMultiplicador(unittest.TestCase):
    def test_multiplicacion_por_uno_es_identidad(self):
        N = 6
        enteros_senal = [round(v * ESCALA) for v in [0.5, -0.5, 0.25, -0.25, 0.0, 1.0]]
        enteros_unos = [ESCALA] * N

        mult = MaquinaMultiplicador("test_mult")
        mult.cargar(enteros_senal, enteros_unos)
        resultado = mult.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)

        esperados = [round(a * b / ESCALA) for a, b in zip(enteros_senal, enteros_unos)]
        self.assertEqual(enteros_salida, esperados)

    def test_multiplicacion_por_cero_da_cero(self):
        enteros_senal = [ESCALA, -ESCALA, 128]
        enteros_ceros = [0, 0, 0]
        mult = MaquinaMultiplicador("test_mult")
        mult.cargar(enteros_senal, enteros_ceros)
        resultado = mult.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertTrue(all(v == 0 for v in enteros_salida))

    def test_maquina_se_detiene_y_acepta(self):
        mult = MaquinaMultiplicador("test_mult")
        mult.cargar([ESCALA, ESCALA], [ESCALA, ESCALA])
        resultado = mult.ejecutar()
        self.assertTrue(resultado.aceptada)

    def test_longitud_salida_coincide_con_entrada(self):
        N = 10
        enteros_senal = [round(math.cos(k * 0.3) * ESCALA) for k in range(N)]
        enteros_portadora = [round(math.cos(k * 0.3) * ESCALA) for k in range(N)]
        mult = MaquinaMultiplicador("test_mult")
        mult.cargar(enteros_senal, enteros_portadora)
        resultado = mult.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertEqual(len(enteros_salida), N)

    def test_requiere_cargar_antes_de_ejecutar(self):
        mult = MaquinaMultiplicador("test_mult")
        with self.assertRaises(RuntimeError):
            mult.ejecutar()

    def test_ejecucion_con_historial_y_pasos_reales(self):
        mult = MaquinaMultiplicador("test_mult")
        mult.cargar([128, -128], [256, 128])
        resultado = mult.ejecutar(registrar_historial=True)
        self.assertGreater(resultado.pasos, 10)
        self.assertGreater(len(resultado.historial), 10)
        salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertEqual(salida, [128, -64])


class TestMaquinaFiltro(unittest.TestCase):
    def test_senal_constante_con_ganancia_unitaria(self):
        constante = [ESCALA] * 10
        filtro = MaquinaFiltro("test_filt", ventana=4, ganancia=1.0)
        filtro.cargar(constante)
        resultado = filtro.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertTrue(all(abs(v - ESCALA) <= 1 for v in enteros_salida))

    def test_longitud_salida_coincide_con_entrada(self):
        N = 8
        enteros_senal = [round(math.sin(k * 0.5) * ESCALA) for k in range(N)]
        filtro = MaquinaFiltro("test_filt", ventana=4, ganancia=2.0)
        filtro.cargar(enteros_senal)
        resultado = filtro.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        self.assertEqual(len(enteros_salida), N)

    def test_maquina_se_detiene_y_acepta(self):
        filtro = MaquinaFiltro("test_filt", ventana=4, ganancia=2.0)
        filtro.cargar([ESCALA, ESCALA, ESCALA, ESCALA])
        resultado = filtro.ejecutar()
        self.assertTrue(resultado.aceptada)

    def test_requiere_cargar_antes_de_ejecutar(self):
        filtro = MaquinaFiltro("test_filt")
        with self.assertRaises(RuntimeError):
            filtro.ejecutar()

    def test_atenuacion_alta_frecuencia(self):
        N = 20
        nyquist = [ESCALA * ((-1) ** k) for k in range(N)]
        filtro = MaquinaFiltro("test_filt", ventana=4, ganancia=1.0)
        filtro.cargar(nyquist)
        resultado = filtro.ejecutar()
        enteros_salida = tokens_enteros_desde_cinta(resultado.contenido_cinta)
        for v in enteros_salida[4:]:
            self.assertLess(abs(v), ESCALA * 0.15)

    def test_ejecucion_pasos_filtro_mayor_a_cero(self):
        filtro = MaquinaFiltro("test_filt", ventana=3, ganancia=2.0)
        filtro.cargar([100, 200, 300])
        resultado = filtro.ejecutar(registrar_historial=True)
        self.assertGreater(resultado.pasos, 20)
        self.assertGreater(len(resultado.historial), 20)


if __name__ == "__main__":
    unittest.main()
