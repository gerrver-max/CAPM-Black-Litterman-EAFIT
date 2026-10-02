# CAPM vs Black-Litterman – EAFIT

## Modelo de optimización de portafolios

Este repositorio contiene un modelo desarrollado en Python para comparar la construcción y optimización de un portafolio mediante dos enfoques:

- Capital Asset Pricing Model (CAPM)
- Black-Litterman

El modelo está diseñado como material académico para el análisis de gestión de portafolios.

---

## 1. Objetivo

El objetivo del ejercicio es comparar cómo diferentes metodologías para estimar los retornos esperados afectan:

- Los retornos esperados de los activos.
- La composición óptima del portafolio.
- La volatilidad.
- El Sharpe Ratio.
- La frontera eficiente.
- La sensibilidad del modelo Black-Litterman frente al nivel de confianza en las opiniones del inversionista.

---

## 2. Activos utilizados

El universo de inversión está compuesto por los siguientes ETFs:

| Ticker | Activo |
|---|---|
| SPY | Acciones Estados Unidos |
| VGK | Acciones Europa |
| EEM | Mercados emergentes |
| BND | Bonos agregados Estados Unidos |
| HYG | Bonos high yield |
| DBC | Commodities |
| GLD | Oro |
| VNQ | REITs Estados Unidos |
| SHY | Bonos Treasury corto plazo |
| LQD | Bonos corporativos investment grade |

---

## 3. Datos

El modelo utiliza datos de mercado con:

- Frecuencia: mensual.
- Periodo de análisis: desde 2020.
- Universo: 10 ETFs.
- Retornos utilizados para la estimación de riesgo: retornos mensuales.
- Matriz de covarianzas: calculada a partir de los retornos mensuales.

El objetivo es mantener una frecuencia consistente entre la estimación de retornos, riesgo y optimización.

---

## 4. Tasa libre de riesgo

La tasa libre de riesgo utilizada en el modelo corresponde al Treasury de Estados Unidos a 5 años (UST 5Y).

El valor se obtiene de información de mercado y se incorpora como tasa anualizada al modelo.

---

## 5. Prima de riesgo

Para el cálculo mediante CAPM se utiliza una prima de riesgo de mercado basada en la metodología de Aswath Damodaran.

La estructura conceptual utilizada es:

    Retorno esperado = Rf + Beta × Prima de riesgo

Esto permite evitar utilizar una prima de riesgo histórica arbitraria y utilizar una referencia ampliamente utilizada en valoración financiera.

---

# 6. CAPM

Los retornos esperados mediante CAPM se calculan como:

    E(Ri) = Rf + βi × ERP

donde:

- E(Ri) = retorno esperado del activo.
- Rf = tasa libre de riesgo.
- βi = beta del activo respecto al mercado.
- ERP = prima de riesgo del mercado.

Estos retornos constituyen los inputs para la optimización del portafolio CAPM.

---

# 7. Black-Litterman

El modelo Black-Litterman parte de los retornos de equilibrio implícitos en el portafolio de referencia.

Los retornos de equilibrio se calculan como:

    Π = Rf + δΣw

donde:

- Π = retornos de equilibrio.
- Rf = tasa libre de riesgo.
- δ = coeficiente de aversión al riesgo.
- Σ = matriz de covarianzas.
- w = pesos del portafolio de referencia.

Posteriormente, las opiniones del inversionista se incorporan mediante el modelo Black-Litterman.

La estructura general utilizada es:

    μBL = [ (τΣ)^-1 + P'Ω^-1P ]^-1
          [ (τΣ)^-1Π + P'Ω^-1Q ]

donde:

- Π = retornos de equilibrio.
- P = matriz de opiniones.
- Q = vector de retornos asociados a las opiniones.
- Ω = matriz de incertidumbre de las opiniones.
- τ = parámetro de incertidumbre asociado a los retornos de equilibrio.

---

# 8. Sensibilidad Black-Litterman

El modelo incluye un análisis de sensibilidad sobre el nivel de confianza asignado a las opiniones.

Se consideran tres escenarios:

| Escenario | Confianza |
|---|---:|
| BL 30% | 30% |
| BL 60% | 60% |
| BL 90% | 90% |

La interpretación es:

### BL 30%

Menor confianza en las opiniones del inversionista.

La incertidumbre Ω aumenta y el modelo otorga mayor peso a los retornos de equilibrio.

### BL 60%

Escenario central utilizado como referencia.

### BL 90%

Mayor confianza en las opiniones del inversionista.

La incertidumbre Ω disminuye y las opiniones tienen mayor influencia sobre los retornos posteriores.

Importante:

> La sensibilidad no modifica el escenario BL Base. Los escenarios BL 30%, BL 60% y BL 90% se utilizan únicamente para estudiar cómo cambia el resultado ante diferentes niveles de confianza.

---

# 9. Optimización

Para cada conjunto de retornos esperados se obtiene un portafolio de máxima razón de Sharpe.

La función objetivo es:

    Max Sharpe Ratio

sujeta a las restricciones definidas en el modelo.

Los portafolios comparados incluyen:

- Benchmark
- CAPM
- Black-Litterman Base
- Black-Litterman 30%
- Black-Litterman 60%
- Black-Litterman 90%

---

# 10. Métricas

Para cada portafolio se calculan:

### Expected Return

Retorno esperado anualizado del portafolio.

### Volatility

Volatilidad anualizada calculada a partir de la matriz de covarianzas.

### Sharpe Ratio

    Sharpe = (E(Rp) - Rf) / σp

donde:

- E(Rp) = retorno esperado del portafolio.
- Rf = tasa libre de riesgo.
- σp = volatilidad del portafolio.

---

# 11. Frontera eficiente

El modelo genera las fronteras eficientes correspondientes a:

- CAPM
- Black-Litterman

Esto permite observar cómo cambia la relación entre riesgo y retorno esperado cuando se utilizan diferentes estimaciones de retornos.

También se identifica el portafolio de máxima razón de Sharpe.

---

# 12. Archivos del repositorio

### `CAPM_vs_Black_Litterman.py`

Script principal del modelo.

Contiene:

- Descarga de datos.
- Preparación de datos mensuales.
- Cálculo de retornos.
- Estimación de riesgo.
- CAPM.
- Retornos de equilibrio.
- Black-Litterman.
- Sensibilidad.
- Optimización.
- Métricas.
- Fronteras eficientes.
- Exportación de resultados.

### `CAPM_vs_Black_Litterman.xlsx`

Archivo Excel generado por el script con los principales resultados del modelo.

### `requirements.txt`

Archivo que contiene las versiones de las principales librerías necesarias para ejecutar el modelo.

### `.gitignore`

Archivo utilizado para evitar subir archivos innecesarios al repositorio, incluyendo el entorno virtual `.venv`.

---

# 13. Requisitos

Se recomienda utilizar:

- Python 3.x
- VS Code
- Terminal

Las principales librerías utilizadas por el modelo son:

- pandas
- numpy
- matplotlib
- scipy
- yfinance
- openpyxl

Las versiones utilizadas en el entorno de referencia se encuentran especificadas en:

    requirements.txt

---

# 14. Instalación

Después de descargar o clonar el repositorio, abrir una terminal dentro de la carpeta del proyecto.

## 14.1 Crear un entorno virtual

### macOS / Linux

    python3 -m venv .venv

### Windows

    py -m venv .venv

---

## 14.2 Activar el entorno virtual

### macOS / Linux

    source .venv/bin/activate

### Windows — PowerShell

    .venv\Scripts\Activate.ps1

### Windows — CMD

    .venv\Scripts\activate.bat

Una vez activado, la terminal mostrará normalmente `(.venv)` al comienzo de la línea.

---

## 14.3 Instalar las dependencias

Con el entorno virtual activado:

    pip install -r requirements.txt

El archivo `requirements.txt` instala las versiones de las librerías utilizadas para desarrollar y probar el modelo.

---

# 15. Ejecución

Con el entorno virtual activado:

    python CAPM_vs_Black_Litterman.py

El programa mostrará en la terminal las diferentes etapas del cálculo y generará los resultados correspondientes.

También se generará el archivo:

    CAPM_vs_Black_Litterman.xlsx

---

# 16. Interpretación académica

El objetivo del ejercicio no es determinar cuál metodología es "correcta", sino analizar cómo los supuestos utilizados para estimar los retornos esperados afectan la construcción del portafolio.

En particular, el ejercicio permite estudiar:

1. La diferencia entre utilizar retornos históricos y retornos esperados.
2. El efecto del CAPM sobre los retornos esperados.
3. La construcción de retornos de equilibrio.
4. La incorporación de opiniones mediante Black-Litterman.
5. El efecto de la incertidumbre sobre dichas opiniones.
6. El impacto de los retornos esperados sobre la optimización.
7. La relación entre riesgo, retorno y Sharpe Ratio.

---

# 17. Preguntas para discusión

Después de ejecutar el modelo, analice:

1. ¿Cómo cambian los retornos esperados entre CAPM y Black-Litterman?

2. ¿Qué activos reciben mayor peso en cada metodología?

3. ¿Por qué el portafolio Black-Litterman puede presentar una composición diferente al portafolio CAPM?

4. ¿Qué ocurre cuando aumenta la confianza en las opiniones?

5. ¿Qué ocurre con los pesos cuando la confianza disminuye?

6. ¿Cómo cambia la frontera eficiente?

7. ¿Qué diferencia existe entre el retorno esperado del portafolio y el retorno histórico?

8. ¿Qué supuestos del modelo pueden explicar las diferencias observadas?

---

# 18. Nota metodológica

Los resultados dependen de:

- El periodo de información utilizado.
- La frecuencia de los datos.
- La matriz de covarianzas.
- La tasa libre de riesgo.
- La prima de riesgo.
- Los parámetros del modelo Black-Litterman.
- Las opiniones incorporadas.
- Las restricciones de optimización.

Por esta razón, los resultados deben interpretarse como una aplicación del modelo bajo un conjunto específico de supuestos y no como una predicción de mercado.

---

## EAFIT

Material académico para el estudio de gestión de portafolios.

CAPM · Black-Litterman · Optimización · Gestión de Portafolios
