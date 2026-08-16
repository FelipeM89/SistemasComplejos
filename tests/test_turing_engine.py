"""
Pruebas para el motor de Maquina de Turing (Cinta, FuncionTransicion, MaquinaDeTuring).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from turing import Tape, TransitionFunction, TuringMachine, BLANK


# ── Cinta ─────────────────────────────────────────────────────────────────────

class TestCinta(unittest.TestCase):
    def test_cinta_vacia_lee_blanco(self):
        tape = Tape()
        self.assertEqual(tape.read(), BLANK)

    def test_escribir_y_leer(self):
        tape = Tape()
        tape.write("1")
        self.assertEqual(tape.read(), "1")

    def test_mover_derecha_y_leer(self):
        tape = Tape(["a", "b", "c"])
        tape.move_right()
        self.assertEqual(tape.read(), "b")

    def test_mover_izquierda_lee_blanco(self):
        tape = Tape(["x"])
        tape.move_left()
        self.assertEqual(tape.read(), BLANK)

    def test_contenido_refleja_escrituras(self):
        tape = Tape(["0", "1"])
        tape.write("9")
        self.assertEqual(tape.content()[0], "9")

    def test_extension_bidireccional(self):
        tape = Tape()
        tape.move_left()
        tape.write("A")
        tape.move_right()
        tape.write("B")
        content = tape.content()
        self.assertIn("A", content)
        self.assertIn("B", content)

    def test_captura_de_estado_snapshot(self):
        tape = Tape(["x"])
        snap = tape.snapshot()
        tape.write("y")
        self.assertEqual(snap["cells"][0], "x")


# ── Funcion de Transicion ─────────────────────────────────────────────────────

class TestFuncionTransicion(unittest.TestCase):
    def test_agregar_y_aplicar(self):
        tf = TransitionFunction()
        tf.add("q0", "0", "q1", "1", "R")
        result = tf.apply("q0", "0")
        self.assertEqual(result.next_state, "q1")
        self.assertEqual(result.write_symbol, "1")
        self.assertEqual(result.direction, "R")

    def test_transicion_no_definida_retorna_none(self):
        tf = TransitionFunction()
        self.assertIsNone(tf.apply("q0", "x"))

    def test_transicion_duplicada_lanza_error(self):
        tf = TransitionFunction()
        tf.add("q0", "0", "q1", "0", "R")
        with self.assertRaises(ValueError):
            tf.add("q0", "0", "q2", "1", "L")

    def test_multiples_reglas(self):
        tf = TransitionFunction([
            ("q0", "a", "q1", "b", "R"),
            ("q1", "b", "q2", "c", "L"),
        ])
        self.assertEqual(tf.apply("q1", "b").next_state, "q2")

    def test_definida_para_par(self):
        tf = TransitionFunction([("q0", "x", "q1", "x", "R")])
        self.assertTrue(tf.defined_for("q0", "x"))
        self.assertFalse(tf.defined_for("q0", "y"))


# ── Maquina de Turing ─────────────────────────────────────────────────────────

def _construir_maquina_incremento() -> TuringMachine:
    """
    MT simple que lee un numero unario y le agrega un '1'.
    Entrada:  1 1 1   (3)
    Salida:   1 1 1 1 (4)
    """
    tf = TransitionFunction([
        ("q_scan", "1", "q_scan", "1", "R"),
        ("q_scan", "_", "q_write", "1", "R"),
        ("q_write", "_", "q_done",  "_", "R"),
    ])
    return TuringMachine(
        name="incremento",
        states={"q_scan", "q_write", "q_done"},
        input_alpha={"1"},
        tape_alpha={"1", "_"},
        transitions=tf,
        initial="q_scan",
        final={"q_done"},
    )


class TestMaquinaDeTuring(unittest.TestCase):
    def test_validacion_estado_inicial_en_Q(self):
        tf = TransitionFunction()
        with self.assertRaises(AssertionError):
            TuringMachine(
                name="invalida",
                states={"q0"},
                input_alpha=set(),
                tape_alpha={"_"},
                transitions=tf,
                initial="q_inicio",
                final={"q0"},
            )

    def test_validacion_estados_finales_subconjunto_Q(self):
        tf = TransitionFunction()
        with self.assertRaises(AssertionError):
            TuringMachine(
                name="invalida",
                states={"q0"},
                input_alpha=set(),
                tape_alpha={"_"},
                transitions=tf,
                initial="q0",
                final={"q_aceptacion"},
            )

    def test_maquina_incremento_correcta(self):
        tm = _construir_maquina_incremento()
        result = tm.run(["1", "1", "1"])
        tape_str = "".join(result.tape_content)
        ones = tape_str.count("1")
        self.assertEqual(ones, 4)

    def test_aceptacion_en_estado_final(self):
        tm = _construir_maquina_incremento()
        result = tm.run(["1"])
        self.assertTrue(result.accepted)

    def test_conteo_de_pasos_positivo(self):
        tm = _construir_maquina_incremento()
        result = tm.run(["1", "1"])
        self.assertGreater(result.steps, 0)

    def test_registro_de_historial(self):
        tm = _construir_maquina_incremento()
        result = tm.run(["1"], record_history=True)
        self.assertGreater(len(result.history), 0)
        self.assertEqual(result.history[0].state, "q_scan")

    def test_limite_maximo_pasos_lanza_error(self):
        tf = TransitionFunction([
            ("q_loop", "_", "q_loop", "_", "R"),
        ])
        tm = TuringMachine(
            name="bucle",
            states={"q_loop", "q_done"},
            input_alpha=set(),
            tape_alpha={"_"},
            transitions=tf,
            initial="q_loop",
            final={"q_done"},
            max_steps=10,
        )
        with self.assertRaises(RuntimeError):
            tm.run([])

    def test_parada_por_transicion_no_definida(self):
        tf = TransitionFunction([
            ("q0", "a", "q1", "a", "R"),
        ])
        tm = TuringMachine(
            name="parada_en_b",
            states={"q0", "q1"},
            input_alpha={"a", "b"},
            tape_alpha={"a", "b", "_"},
            transitions=tf,
            initial="q0",
            final={"q1"},
        )
        result = tm.run(["a", "b"])
        self.assertEqual(result.steps, 1)


if __name__ == "__main__":
    unittest.main()
