# Sistema de Comunicación Digital con Máquinas de Turing

**Autor:** [FelipeM89](https://github.com/FelipeM89)  
**Materia:** Sistemas Complejos  

---

## 📌 Resumen del Proyecto

Este proyecto implementa una simulación ejecutable y formal de un **Sistema de Comunicación Digital** donde el procesamiento y transformación de la información es realizado por una composición secuencial de **Máquinas de Turing Deterministas (MT)**.

El flujo representa el modelo clásico de modulación y demodulación en banda base (**DSB-SC**):

```
       TRANSMISOR (Tx)                     RECEPTOR (Rx)
       ───────────────                     ─────────────
  x[n] ──→ [MT_MULT_TX] ──→ x[n]cos(ωn) ──→ CANAL ──→ [MT_MULT_RX] ──→ [MT_FILTER] ──→ x̂[n]
                 ↑                                           ↑
            [MT_OSC_TX]                                 [MT_OSC_RX]
```

---

## ⚙️ ¿Qué se hizo? (Componentes del Sistema)

1. **Motor Formal de Máquina de Turing ($M = \langle Q, \Sigma, \Gamma, \delta, q_0, F \rangle$):**
   - **Cinta infinita bidireccional** con símbolo blanco `_`.
   - **Función de transición determinista** $\delta: (q, s) \to (q', s', \text{dir})$.
   - Control de pasos máximos y registro de configuraciones paso a paso.

2. **Representación Discreta en Cinta (Punto Fijo Q8):**
   - Muestras continuas discretizadas a enteros: $\text{entero} = \text{round}(\text{valor} \times 256)$.
   - Alfabeto en cinta: $\Sigma = \{0..9, -, |, \_\}$. Formato: `| v0 | v1 | v2 | ... | vn |`.

3. **Las 5 Máquinas de Turing + Medio Físico:**
   - **MT 2 — `MT_OSC_TX` (Oscilador Tx):** Genera la portadora discreta $\cos(\omega \cdot n)$ en su cinta.
   - **MT 1 — `MT_MULT_TX` (Multiplicador Tx):** Multiplica la señal de entrada $x[n]$ por la portadora.
   - **`CANAL` (Medio Físico):** Modelado físico separado (ideal, atenuado o con ruido gaussiano $\sigma$).
   - **MT 4 — `MT_OSC_RX` (Oscilador Rx):** Genera la portadora del receptor $\cos(\omega_{rx} \cdot n)$.
   - **MT 3 — `MT_MULT_RX` (Multiplicador Rx):** Demodula la señal recibida: $y[n] \cdot \cos(\omega_{rx} n)$.
   - **MT 5 — `MT_FILTER` (Filtro Pasa-Bajos):** Elimina la componente de alta frecuencia $2\omega$ mediante promedio móvil causal y aplica compensación de ganancia $\times 2$.

---

## 📁 Estructura del Código

```
SistemasComplejos/
│
├── principal.py                     # Punto de entrada principal en español
├── main.py                          # Enlace de compatibilidad
├── requirements.txt                 # Dependencias (numpy, matplotlib, pytest)
├── .gitignore                       # Filtro de archivos para Git
│
├── turing/                          # Motor formal de Máquina de Turing
│   ├── cinta.py                     # Clase Cinta (lectura, escritura, movimiento L/R)
│   ├── transicion.py                # Clase FuncionTransicion
│   ├── maquina.py                   # Clase MaquinaDeTuring y ResultadoEjecucion
│   └── __init__.py
│
├── codificacion/                    # Representación y formateo en cinta
│   ├── codificacion_senal.py        # Codificación y decodificación punto fijo Q8
│   └── __init__.py
│
├── maquinas/                        # Bloques computacionales de MTs y canal
│   ├── oscilador.py                 # MaquinaOscilador (MT 2 y MT 4)
│   ├── multiplicador.py             # MaquinaMultiplicador (MT 1 y MT 3)
│   ├── filtro.py                    # MaquinaFiltro (MT 5)
│   ├── canal.py                     # Modelo del medio físico
│   └── __init__.py
│
├── comunicacion/                    # Canalización y composición del sistema
│   ├── sistema.py                   # Clase SistemaComunicacion
│   └── __init__.py
│
├── visualizacion/                   # Gráficos con Matplotlib
│   ├── graficos.py                  # Gráficos de canalización y error
│   └── __init__.py
│
└── pruebas/                         # Suite de pruebas automatizadas (100% pasando)
    ├── test_motor_turing.py
    ├── test_maquinas.py
    ├── test_sistema.py
    └── __init__.py
```

---

## 🚀 Instrucciones de Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la simulación principal
```bash
# Modo con gráficos en pantalla
python principal.py

# Modo solo consola (sin ventanas emergentes)
python principal.py --sin-graficos

# Simulación con ruido en el canal
python principal.py --ruido --sin-graficos

# Simulación con desajuste de frecuencia (ω_rx ≠ ω_tx)
python principal.py --desajuste --sin-graficos
```

### 3. Ejecutar pruebas automatizadas
```bash
python -m pytest -v
```

---

## 📊 Resultados de Fidelidad

- **MAE (Error Absoluto Medio):** $\approx 0.06$ (Calidad Excelente)
- **MSE (Error Cuadrático Medio):** $\approx 0.005$
- **Pruebas unitarias e integración:** 102/102 pruebas exitosas.
