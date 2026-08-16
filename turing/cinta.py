"""
Cinta — cinta infinita bidireccional para maquinas de Turing.

La cinta esta indexada por enteros; las posiciones no escritas contienen
el simbolo blanco.
"""

from collections import defaultdict

BLANCO = "_"
BLANK = BLANCO  # Alias de compatibilidad


class Cinta:
    """Cinta infinita bidireccional con cabezal de lectura/escritura."""

    def __init__(self, simbolos: list[str] | None = None, blanco: str = BLANCO):
        self.blanco = blanco
        self.blank = blanco
        self._celdas: dict[int, str] = defaultdict(lambda: self.blanco)
        self.cabezal: int = 0
        self.head: int = 0

        if simbolos:
            for i, sim in enumerate(simbolos):
                self._celdas[i] = sim

    # ------------------------------------------------------------------
    # Operaciones del cabezal
    # ------------------------------------------------------------------

    def leer(self) -> str:
        """Lee el simbolo bajo el cabezal actual."""
        return self._celdas[self.cabezal]

    def read(self) -> str:
        return self.leer()

    def escribir(self, simbolo: str) -> None:
        """Escribe un simbolo en la posicion actual del cabezal."""
        self._celdas[self.cabezal] = simbolo

    def write(self, symbol: str) -> None:
        self.escribir(symbol)

    def mover_izquierda(self) -> None:
        """Desplaza el cabezal una posicion a la izquierda."""
        self.cabezal -= 1
        self.head = self.cabezal

    def move_left(self) -> None:
        self.mover_izquierda()

    def mover_derecha(self) -> None:
        """Desplaza el cabezal una posicion a la derecha."""
        self.cabezal += 1
        self.head = self.cabezal

    def move_right(self) -> None:
        self.mover_derecha()

    def mover(self, direccion: str) -> None:
        """Mueve el cabezal en la direccion indicada ('L' o 'R')."""
        if direccion == "R":
            self.mover_derecha()
        elif direccion == "L":
            self.mover_izquierda()
        else:
            raise ValueError(f"Direccion desconocida: {direccion!r}")

    def move(self, direction: str) -> None:
        self.mover(direction)

    # ------------------------------------------------------------------
    # Acceso al contenido
    # ------------------------------------------------------------------

    def contenido(self) -> list[str]:
        """Retorna las celdas no vacias en orden de posicion."""
        if not self._celdas:
            return [self.blanco]
        minimo, maximo = min(self._celdas), max(self._celdas)
        return [self._celdas[i] for i in range(minimo, maximo + 1)]

    def content(self) -> list[str]:
        return self.contenido()

    def contenido_cadena(self) -> str:
        """Retorna el contenido de la cinta como cadena de texto."""
        return "".join(self.contenido())

    def content_str(self) -> str:
        return self.contenido_cadena()

    def captura(self) -> dict:
        """Captura el estado actual del cabezal y celdas."""
        return {"cabezal": self.cabezal, "celdas": dict(self._celdas)}

    def snapshot(self) -> dict:
        return {"head": self.cabezal, "cells": dict(self._celdas)}

    def reiniciar_cabezal(self) -> None:
        """Reinicia el cabezal a la posicion minima registrada."""
        self.cabezal = min(self._celdas.keys(), default=0)
        self.head = self.cabezal

    def reset_head(self) -> None:
        self.reiniciar_cabezal()

    def __repr__(self) -> str:
        celdas = self.contenido()
        minimo = min(self._celdas.keys(), default=0)
        indice = self.cabezal - minimo
        anotadas = celdas[:]
        if 0 <= indice < len(anotadas):
            anotadas[indice] = f"[{anotadas[indice]}]"
        return "Cinta(" + "".join(anotadas) + ")"


Tape = Cinta
