# Sistema de Comunicación Digital con Máquinas de Turing

**Autor:** [FelipeM89](https://github.com/FelipeM89)  
**Materia:** Sistemas Complejos  

---

## 1. Resumen del Proyecto

Este proyecto implementa una simulación formal y ejecutable de un **Sistema de Comunicación Digital** en el cual todo el procesamiento computacional de la señal (generación de portadora, modulación, demodulación y filtrado) es realizado por una composición secuencial de **Máquinas de Turing Deterministas (MT)**.

El sistema modela el esquema de modulación en amplitud con portadora suprimida (DSB-SC):

```
       TRANSMISOR (Tx)                     RECEPTOR (Rx)
       ---------------                     -------------
  x[n] ---> [MT_MULT_TX] ---> x[n]cos(ωn) ---> CANAL ---> [MT_MULT_RX] ---> [MT_FILTER] ---> x^[n]
                 ^                                             ^
            [MT_OSC_TX]                                   [MT_OSC_RX]
```

---

## 2. Arquitectura y Componentes

### A. Motor Formal de Máquina de Turing
Se implementó un simulador determinista basado en la definición formal $M = (Q, \Sigma, \Gamma, \delta, q_0, F)$:
- **Cinta infinita bidireccional:** con soporte de lectura, escritura y desplazamientos `L`/`R`.
- **Función de transición:** $\delta: (q, s) \to (q', s', \text{dir})$.
- **Validador formal:** verificación de pertenencia de estados, alfabetos y condiciones de parada.

### B. Representación Discreta en Cinta (Punto Fijo Q8)
- Cada muestra se cuantiza en formato de punto fijo Q8: `entero = round(valor * 256)`.
- En la cinta, cada muestra se escribe en base 10 delimitada por el separador `|`.

Ejemplo de cinta:
```
+---+-----+---+-----+---+------+---+------+---+
| | | 256 | | | 138 | | | -107 | | | -253 | | | ...
+---+-----+---+-----+---+------+---+------+---+
```

### C. Bloques Computacionales (5 Máquinas de Turing y Canal)
1. **MT 2 — MT_OSC_TX (Oscilador del Transmisor):** Genera la portadora discreta $\cos(\omega n)$ escribiendo cada dígito en su cinta mediante su ciclo de estados.
2. **MT 1 — MT_MULT_TX (Multiplicador del Transmisor):** Lee los pares de operandos de la cinta, calcula el producto $x[n] \times \cos(\omega n)$ y ajusta la escala Q8 en la cinta.
3. **CANAL (Medio Físico):** Modelo del canal de propagación (ideal, atenuado o con ruido gaussiano).
4. **MT 4 — MT_OSC_RX (Oscilador del Receptor):** Genera la portadora de demodulación $\cos(\omega_{\text{rx}} n)$.
5. **MT 3 — MT_MULT_RX (Multiplicador del Receptor):** Produce $y[n] \times \cos(\omega_{\text{rx}} n)$ mediante transiciones sobre la cinta.
6. **MT 5 — MT_FILTER (Filtro Pasa-Bajos):** Promedio móvil causal que recorre la ventana deslizante sobre la cinta, elimina la componente de alta frecuencia ($2\omega$) y aplica ganancia $\times 2$.

---

## 3. Estructura del Repositorio

```
SistemasComplejos/
│
├── principal.py                     # Punto de entrada principal
├── requirements.txt                 # Dependencias (numpy, matplotlib, pytest)
├── README.md                        # Documentación en español
├── .gitignore                       # Exclusión de archivos temporales
│
├── turing/                          # Motor formal de Máquina de Turing
│   ├── cinta.py                     # Clase Cinta
│   ├── transicion.py                # Clase FuncionTransicion
│   ├── maquina.py                   # Clase MaquinaDeTuring y ResultadoEjecucion
│   └── __init__.py
│
├── codificacion/                    # Representación Q8 y cinta
│   ├── codificacion_senal.py        # Codificador/decodificador de cinta
│   └── __init__.py
│
├── maquinas/                        # Bloques de MTs y canal
│   ├── oscilador.py                 # MaquinaOscilador (MT 2 y MT 4)
│   ├── multiplicador.py             # MaquinaMultiplicador (MT 1 y MT 3)
│   ├── filtro.py                    # MaquinaFiltro (MT 5)
│   ├── canal.py                     # Modelo del medio físico
│   └── __init__.py
│
├── comunicacion/                    # Canalización completa
│   ├── sistema.py                   # Clase SistemaComunicacion
│   └── __init__.py
│
├── visualizacion/                   # Gráficos con Matplotlib
│   ├── graficos.py                  # Visualización de señales y métricas de error
│   └── __init__.py
│
└── pruebas/                         # Suite de pruebas automatizadas
    ├── test_motor_turing.py         # Pruebas del motor formal
    ├── test_maquinas.py             # Pruebas de las 5 MTs
    ├── test_sistema.py              # Pruebas de integración del sistema
    └── __init__.py
```

---

## 4. Instrucciones de Ejecución

### Instalación de dependencias
```bash
pip install -r requirements.txt
```

### Ejecución de la simulación
```bash
# Modo con gráficos en pantalla
python principal.py

# Modo consola (sin interfaz gráfica)
python principal.py --sin-graficos

# Modo canal con ruido gaussiano
python principal.py --ruido --sin-graficos

# Modo desajuste de frecuencia (omega_rx != omega_tx)
python principal.py --desajuste --sin-graficos
```

### Ejecución de pruebas automatizadas
```bash
python -m unittest discover -s pruebas
```
o con pytest:
```bash
pytest pruebas/
```

---

## 5. Métricas de Fidelidad

- **MAE (Error Absoluto Medio):** ~0.06 (Calidad Excelente)
- **MSE (Error Cuadrático Medio):** ~0.005
- **Pruebas automatizadas:** 54/54 pruebas exitosas.
