"""
Pruebas para el motor de Maquina de Turing (Cinta, FuncionTransicion, MaquinaDeTuring).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from turing import Cinta, FuncionTransicion, MaquinaDeTuring, BLANCO


class TestCinta(unittest.TestCase):
    def test_cinta_vacia_lee_blanco(self):
        cinta = Cinta()
        self.assertEqual(cinta.leer(), BLANCO)

    def test_escribir_y_leer(self):
        cinta = Cinta()
        cinta.escribir("1")
        self.assertEqual(cinta.leer(), "1")

    def test_mover_derecha_y_leer(self):
        cinta = Cinta(["a", "b", "c"])
        cinta.mover_derecha()
        self.assertEqual(cinta.leer(), "b")

    def test_mover_izquierda_lee_blanco(self):
        cinta = Cinta(["x"])
        cinta.mover_izquierda()
        self.assertEqual(cinta.leer(), BLANCO)

    def test_contenido_refleja_escrituras(self):
        cinta = Cinta(["0", "1"])
        cinta.escribir("9")
        self.assertEqual(cinta.contenido()[0], "9")

    def test_extension_bidireccional(self):
        cinta = Cinta()
        cinta.mover_izquierda()
        cinta.escribir("A")
        cinta.mover_derecha()
        cinta.escribir("B")
        contenido = cinta.contenido()
        self.assertIn("A", contenido)
        self.assertIn("B", contenido)

    def test_captura_de_estado_snapshot(self):
        cinta = Cinta(["x"])
        captura = cinta.captura()
        cinta.escribir("y")
        self.assertEqual(captura["celdas"][0], "x")


class TestFuncionTransicion(unittest.TestCase):
    def test_agregar_y_aplicar(self):
        ft = FuncionTransicion()
        ft.agregar("q0", "0", "q1", "1", "R")
        resultado = ft.aplicar("q0", "0")
        self.assertEqual(resultado.siguiente_estado, "q1")
        self.assertEqual(resultado.simbolo_escritura, "1")
        self.assertEqual(resultado.direccion, "R")

    def test_transicion_no_definida_retorna_none(self):
        ft = FuncionTransicion()
        self.assertIsNone(ft.aplicar("q0", "x"))

    def test_transicion_duplicada_lanza_error(self):
        ft = FuncionTransicion()
        ft.agregar("q0", "0", "q1", "0", "R")
        with self.assertRaises(ValueError):
            ft.agregar("q0", "0", "q2", "1", "L")

    def test_multiples_reglas(self):
        ft = FuncionTransicion([
            ("q0", "a", "q1", "b", "R"),
            ("q1", "b", "q2", "c", "L"),
        ])
        self.assertEqual(ft.aplicar("q1", "b").siguiente_estado, "q2")

    def test_definida_para_par(self):
        ft = FuncionTransicion([("q0", "x", "q1", "x", "R")])
        self.assertTrue(ft.definida_para("q0", "x"))
        self.assertFalse(ft.definida_para("q0", "y"))


def _construir_maquina_incremento() -> MaquinaDeTuring:
    ft = FuncionTransicion([
        ("q_scan", "1", "q_scan", "1", "R"),
        ("q_scan", "_", "q_write", "1", "R"),
        ("q_write", "_", "q_done",  "_", "R"),
    ])
    return MaquinaDeTuring(
        nombre="incremento",
        estados={"q_scan", "q_write", "q_done"},
        alfabeto_entrada={"1"},
        alfabeto_cinta={"1", "_"},
        transiciones=ft,
        estado_inicial="q_scan",
        estados_finales={"q_done"},
    )


class TestMaquinaDeTuring(unittest.TestCase):
    def test_validacion_estado_inicial_en_Q(self):
        ft = FuncionTransicion()
        with self.assertRaises(AssertionError):
            MaquinaDeTuring(
                nombre="invalida",
                estados={"q0"},
                alfabeto_entrada=set(),
                alfabeto_cinta={"_"},
                transiciones=ft,
                estado_inicial="q_inicio",
                estados_finales={"q0"},
            )

    def test_validacion_estados_finales_subconjunto_Q(self):
        ft = FuncionTransicion()
        with self.assertRaises(AssertionError):
            MaquinaDeTuring(
                nombre="invalida",
                estados={"q0"},
                alfabeto_entrada=set(),
                alfabeto_cinta={"_"},
                transiciones=ft,
                estado_inicial="q0",
                estados_finales={"q_aceptacion"},
            )

    def test_maquina_incremento_correcta(self):
        mt = _construir_maquina_incremento()
        resultado = mt.ejecutar(["1", "1", "1"])
        cadena_cinta = "".join(resultado.contenido_cinta)
        unos = cadena_cinta.count("1")
        self.assertEqual(unos, 4)

    def test_aceptacion_en_estado_final(self):
        mt = _construir_maquina_incremento()
        resultado = mt.ejecutar(["1"])
        self.assertTrue(resultado.aceptada)

    def test_conteo_de_pasos_positivo(self):
        mt = _construir_maquina_incremento()
        resultado = mt.ejecutar(["1", "1"])
        self.assertGreater(resultado.pasos, 0)

    def test_registro_de_historial(self):
        mt = _construir_maquina_incremento()
        resultado = mt.ejecutar(["1"], registrar_historial=True)
        self.assertGreater(len(resultado.historial), 0)
        self.assertEqual(resultado.historial[0].estado, "q_scan")

    def test_limite_maximo_pasos_lanza_error(self):
        ft = FuncionTransicion([
            ("q_loop", "_", "q_loop", "_", "R"),
        ])
        mt = MaquinaDeTuring(
            nombre="bucle",
            estados={"q_loop", "q_done"},
            alfabeto_entrada=set(),
            alfabeto_cinta={"_"},
            transiciones=ft,
            estado_inicial="q_loop",
            estados_finales={"q_done"},
            max_pasos=10,
        )
        with self.assertRaises(RuntimeError):
            mt.ejecutar([])

    def test_parada_por_transicion_no_definida(self):
        ft = FuncionTransicion([
            ("q0", "a", "q1", "a", "R"),
        ])
        mt = MaquinaDeTuring(
            nombre="parada_en_b",
            estados={"q0", "q1"},
            alfabeto_entrada={"a", "b"},
            alfabeto_cinta={"a", "b", "_"},
            transiciones=ft,
            estado_inicial="q0",
            estados_finales={"q1"},
        )
        resultado = mt.ejecutar(["a", "b"])
        self.assertEqual(resultado.pasos, 1)


if __name__ == "__main__":
    unittest.main()
