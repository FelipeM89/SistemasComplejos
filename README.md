# Sistema de Comunicacion Digital con Maquinas de Turing

**Autor:** [FelipeM89](https://github.com/FelipeM89)  
**Materia:** Sistemas Complejos  

---

## 1. Resumen del Proyecto

Este proyecto implementa una simulacion formal y ejecutable de un **Sistema de Comunicacion Digital** en el cual todo el procesamiento computacional de la senal (generacion de portadora, modulacion, demodulacion y filtrado) es realizado por una composicion secuencial de **Maquinas de Turing Deterministas (MT)**.

El sistema modela el esquema de modulacion en amplitud con portadora suprimida (DSB-SC):

```
       TRANSMISOR (Tx)                     RECEPTOR (Rx)
       ---------------                     -------------
  x[n] ---> [MT_MULT_TX] ---> x[n]cos(wn) ---> CANAL ---> [MT_MULT_RX] ---> [MT_FILTER] ---> x^[n]
                 ^                                             ^
            [MT_OSC_TX]                                   [MT_OSC_RX]
```

---

## 2. Que se hizo (Arquitectura y Componentes)

### A. Motor Formal de Maquina de Turing
Se implemento un simulador universal determinista basado en la definicion formal M = (Q, Sigma, Gamma, delta, q0, F):
- **Cinta infinita bidireccional:** con soporte de lectura, escritura y desplazamientos L/R.
- **Funcion de transicion:** delta: (estado_actual, simbolo_leido) -> (siguiente_estado, simbolo_escritura, direccion).
- **Validador formal:** verificacion de pertenencia de estados, alfabetos y condiciones de parada.

### B. Representacion Discreta en Cinta (Punto Fijo Q8)
Para resolver la diferencia entre senales matematicas continuas y simbolos discretos de una MT:
- Cada muestra se cuantiza en formato de punto fijo Q8: `entero = round(valor * 256)`.
- En la cinta, cada muestra se escribe en base 10 (con signo '-' si es negativa) delimitada por el separador '|'.

Ejemplo de disposicion de la cinta:
```
+---+-----+---+-----+---+------+---+------+---+
| | | 256 | | | 138 | | | -107 | | | -253 | | | ...
+---+-----+---+-----+---+------+---+------+---+
```

### C. Bloques Computacionales (5 Maquinas de Turing y Canal)
1. **MT 2 — MT_OSC_TX (Oscilador del Transmisor):** Genera la portadora discreta cos(w*n) escribiendo los digitos en su cinta.
2. **MT 1 — MT_MULT_TX (Multiplicador del Transmisor):** Calcula el producto x[n] * cos(w*n) y ajusta la escala Q8.
3. **CANAL (Medio Fisico):** Modelo del canal de propagacion (ideal, atenuado o con ruido gaussiano). Se separa academicamente del modelo de computo de las MTs.
4. **MT 4 — MT_OSC_RX (Oscilador del Receptor):** Genera la portadora de demodulacion cos(w_rx*n).
5. **MT 3 — MT_MULT_RX (Multiplicador del Receptor):** Produce y[n] * cos(w_rx*n) = x[n] * (1 + cos(2wn)) / 2.
6. **MT 5 — MT_FILTER (Filtro Pasa-Bajos):** Promedio movil causal que elimina la componente de doble frecuencia (2w) y aplica compensacion de ganancia x2.

---

## 3. Estructura del Repositorio

```
SistemasComplejos/
│
├── principal.py                     # Punto de entrada principal en espanol
├── main.py                          # Enlace de compatibilidad
├── requirements.txt                 # Dependencias (numpy, matplotlib, pytest)
├── .gitignore                       # Exclusion de temporales
│
├── turing/                          # Motor formal de Maquina de Turing
│   ├── cinta.py                     # Clase Cinta
│   ├── transicion.py                # Clase FuncionTransicion
│   ├── maquina.py                   # Clase MaquinaDeTuring y ResultadoEjecucion
│   └── __init__.py
│
├── codificacion/                    # Representacion Q8 y cinta
│   ├── codificacion_senal.py        # Codificador/decodificador de cinta
│   └── __init__.py
│
├── maquinas/                        # Bloques de MTs y canal
│   ├── oscilador.py                 # MaquinaOscilador (MT 2 y MT 4)
│   ├── multiplicador.py             # MaquinaMultiplicador (MT 1 y MT 3)
│   ├── filtro.py                    # MaquinaFiltro (MT 5)
│   ├── canal.py                     # Modelo del medio fisico
│   └── __init__.py
│
├── comunicacion/                    # Canalizacion completa
│   ├── sistema.py                   # Clase SistemaComunicacion
│   └── __init__.py
│
├── visualizacion/                   # Graficos con Matplotlib
│   ├── graficos.py                  # Generador de graficos de senales y error
│   └── __init__.py
│
└── pruebas/                         # Suite de pruebas automatizadas
    ├── test_motor_turing.py
    ├── test_maquinas.py
    ├── test_sistema.py
    └── __init__.py
```

---

## 4. Instrucciones de Ejecucion

### Instalacion de dependencias
```bash
pip install -r requirements.txt
```

### Ejecucion de la simulacion
```bash
# Modo con graficos en pantalla
python principal.py

# Modo solo consola (sin interfaz grafica)
python principal.py --sin-graficos

# Modo canal con ruido gaussiano
python principal.py --ruido --sin-graficos

# Modo desajuste de frecuencia (omega_rx != omega_tx)
python principal.py --desajuste --sin-graficos
```

### Ejecucion de pruebas automatizadas
```bash
python -m pytest -v
```

---

## 5. Metricas de Fidelidad

- **MAE (Error Absoluto Medio):** ~0.06 (Calidad Excelente)
- **MSE (Error Cuadratico Medio):** ~0.005
- **Pruebas automatizadas:** 102/102 pruebas exitosas.
