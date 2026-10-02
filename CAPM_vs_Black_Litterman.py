# ============================================================
# OPTIMIZACIÓN DE PORTAFOLIO
# CAPM vs BLACK-LITTERMAN
#
# DATOS MENSUALES
# DESDE ENERO DE 2020
#
# BL BASE + SENSIBILIDAD 30%, 60%, 90%
# ============================================================


# ============================================================
# 1. LIBRERÍAS
# ============================================================

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from scipy.optimize import minimize


# ============================================================
# 2. ACTIVOS
# ============================================================

TICKERS = [
    "SPY",
    "VGK",
    "EEM",
    "BND",
    "HYG",
    "DBC",
    "GLD",
    "VNQ",
    "SHY",
    "LQD"
]


# ============================================================
# 3. PARÁMETROS
# ============================================================

START_DATE = "2020-01-01"

END_DATE = (
    pd.Timestamp.today()
    + pd.Timedelta(days=1)
).strftime("%Y-%m-%d")


# Prima de riesgo de mercado de Damodaran
ERP_DAMODARAN = 0.0414


# Aversión al riesgo
DELTA = 2.5


# Tau
TAU = 0.05


# Peso máximo por activo
MAX_WEIGHT = 0.30


# ============================================================
# 4. BENCHMARK
# ============================================================

BENCHMARK_WEIGHTS = np.array([
    0.25,   # SPY
    0.10,   # VGK
    0.10,   # EEM
    0.15,   # BND
    0.05,   # HYG
    0.05,   # DBC
    0.10,   # GLD
    0.05,   # VNQ
    0.05,   # SHY
    0.10    # LQD
])


# ============================================================
# 5. DESCARGA DIRECTA DE DATOS MENSUALES
# ============================================================

print("\n")
print("=" * 70)
print("1. DESCARGANDO DATOS MENSUALES")
print("=" * 70)


data = yf.download(
    TICKERS,
    start=START_DATE,
    end=END_DATE,
    interval="1mo",
    auto_adjust=True,
    progress=False
)


if isinstance(data.columns, pd.MultiIndex):
    prices = data["Close"]
else:
    prices = data.copy()


prices = prices[TICKERS].dropna()


print("\nDatos descargados correctamente.")

print(
    "Período:",
    prices.index[0].date(),
    "hasta",
    prices.index[-1].date()
)

print(
    "Observaciones mensuales:",
    len(prices)
)


# ============================================================
# 6. RETORNOS MENSUALES
# ============================================================

print("\n")
print("=" * 70)
print("2. CALCULANDO RETORNOS MENSUALES")
print("=" * 70)


returns_monthly = (
    prices
    .pct_change()
    .dropna()
)


print(
    "\nObservaciones de retornos:",
    len(returns_monthly)
)

print(
    "Período:",
    returns_monthly.index[0].date(),
    "hasta",
    returns_monthly.index[-1].date()
)


# ============================================================
# 7. RETORNOS HISTÓRICOS ANUALIZADOS
# ============================================================

historical_returns = (
    (1 + returns_monthly)
    .prod()
    ** (12 / len(returns_monthly))
    - 1
)


# ============================================================
# 8. MATRIZ DE COVARIANZAS ANUALIZADA
# ============================================================

Sigma = (
    returns_monthly.cov()
    * 12
)


# ============================================================
# 9. UST 5Y ACTUAL
# ============================================================

print("\n")
print("=" * 70)
print("3. OBTENIENDO UST 5Y")
print("=" * 70)


try:

    fred_url = (
        "https://fred.stlouisfed.org/graph/"
        "fredgraph.csv?id=DGS5"
    )

    ust_data = pd.read_csv(
        fred_url,
        parse_dates=["observation_date"]
    )

    ust_data = ust_data.rename(
        columns={
            "observation_date": "Date",
            "DGS5": "UST5Y"
        }
    )

    ust_data["UST5Y"] = pd.to_numeric(
        ust_data["UST5Y"],
        errors="coerce"
    )

    ust_data = ust_data.dropna(
        subset=["UST5Y"]
    )

    last_ust = ust_data.iloc[-1]

    rf = last_ust["UST5Y"] / 100

    rf_date = last_ust["Date"].date()

except Exception as e:

    print("\nNo fue posible obtener UST 5Y.")

    print("Se utilizará 5.09% como valor de respaldo.")

    print("Error:", e)

    rf = 0.0509

    rf_date = "fallback"


print(
    "\nUST 5Y:",
    f"{rf:.2%}"
)

print(
    "Fecha:",
    rf_date
)


# ============================================================
# 10. CAPM
# ============================================================

print("\n")
print("=" * 70)
print("4. CAPM")
print("=" * 70)


market_returns = returns_monthly["SPY"]


market_variance = (
    market_returns.var()
)


# Beta de cada activo respecto a SPY

betas = returns_monthly.apply(
    lambda x:
    x.cov(market_returns)
    / market_variance
)


# CAPM:
#
# E(Ri) = Rf + Beta_i * ERP

capm_returns = (
    rf
    + betas * ERP_DAMODARAN
)


print(
    "\nPrima de riesgo Damodaran:",
    f"{ERP_DAMODARAN:.2%}"
)


print("\nRetornos CAPM:")

print(
    capm_returns.to_string(
        float_format=lambda x:
        f"{x:.2%}"
    )
)


# ============================================================
# 11. BLACK-LITTERMAN
# ============================================================

print("\n")
print("=" * 70)
print("5. BLACK-LITTERMAN")
print("=" * 70)


# Retornos de equilibrio:
#
# Pi = delta * Sigma * w

Pi = pd.Series(
    rf
    + DELTA
    * Sigma.values.dot(
        BENCHMARK_WEIGHTS
    ),
    index=TICKERS,
    name="Equilibrium"
)

print("\nPI EQUILIBRIO:")
print(Pi.to_string(float_format=lambda x: f"{x:.2%}"))

print("\nRetornos de equilibrio:")

print(
    Pi.to_string(
        float_format=lambda x:
        f"{x:.2%}"
    )
)


# ============================================================
# 12. VIEWS
# ============================================================

print("\n")
print("=" * 70)
print("6. VIEWS")
print("=" * 70)


# View absoluta 1:
# SPY = 8%

# View absoluta 2:
# GLD = 6%

# View relativa 1:
# EEM - SPY = 2%

# View relativa 2:
# VGK - SPY = 1%


P = np.array([

    # SPY
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    # GLD
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],

    # EEM - SPY
    [-1, 0, 1, 0, 0, 0, 0, 0, 0, 0],

    # VGK - SPY
    [-1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

])


Q = np.array([
    0.08,
    0.06,
    0.02,
    0.01
])


print("\nViews:")

print("SPY       = 8.00%")
print("GLD       = 6.00%")
print("EEM-SPY   = 2.00%")
print("VGK-SPY   = 1.00%")


# ============================================================
# 13. OMEGA BASE
# ============================================================

# Esta es la especificación BASE.
#
# NO introducimos sensibilidad aquí.
#
# Omega = diag(P * tau*Sigma * P')

Omega_base = np.diag(
    np.diag(
        P
        @ (0.20 * Sigma.values)
        @ P.T
    )
)


# ============================================================
# 14. FUNCIÓN BLACK-LITTERMAN
# ============================================================

def calculate_black_litterman(
    Pi,
    Sigma,
    P,
    Q,
    tau,
    Omega
):

    tau_sigma = (
        tau * Sigma
    )


    tau_sigma_inverse = np.linalg.pinv(
        tau_sigma
    )


    omega_inverse = np.linalg.pinv(
        Omega
    )


    posterior_precision = (
        tau_sigma_inverse
        +
        P.T
        @ omega_inverse
        @ P
    )


    posterior_covariance = np.linalg.pinv(
        posterior_precision
    )


    posterior_returns = (
        posterior_covariance
        @
        (
            tau_sigma_inverse
            @ Pi.values
            +
            P.T
            @ omega_inverse
            @ Q
        )
    )


    return pd.Series(
        posterior_returns,
        index=TICKERS
    )


# ============================================================
# 15. BL BASE
# ============================================================

bl_base = calculate_black_litterman(
    Pi,
    Sigma.values,
    P,
    Q,
    TAU,
    Omega_base
)


bl_base.name = "BL Base"


# ============================================================
# 16. SENSIBILIDAD
# ============================================================

# IMPORTANTE:
#
# La sensibilidad NO modifica el BL BASE.
#
# El BL BASE se mantiene intacto.
#
# Para la sensibilidad:
#
# 30% = menor confianza
# 60% = confianza intermedia
# 90% = mayor confianza
#
# El punto 60% se toma como referencia para el análisis
# de sensibilidad.
# ============================================================


def calculate_omega_sensitivity(
    Omega_base,
    confidence
):

    # El punto central es 60%.
    #
    # A menor confianza:
    # mayor incertidumbre -> Omega mayor.
    #
    # A mayor confianza:
    # menor incertidumbre -> Omega menor.

    scaling_factor = (
        0.60 / confidence
    )

    return (
        Omega_base *
        scaling_factor
    )


# ------------------------------------------------------------
# 30%
# ------------------------------------------------------------

Omega_30 = calculate_omega_sensitivity(
    Omega_base,
    0.30
)


bl_30 = calculate_black_litterman(
    Pi,
    Sigma.values,
    P,
    Q,
    TAU,
    Omega_30
)

bl_30.name = "BL 30%"


# ------------------------------------------------------------
# 60%
# ------------------------------------------------------------

Omega_60 = calculate_omega_sensitivity(
    Omega_base,
    0.60
)


bl_60 = calculate_black_litterman(
    Pi,
    Sigma.values,
    P,
    Q,
    TAU,
    Omega_60
)

bl_60.name = "BL 60%"


# ------------------------------------------------------------
# 90%
# ------------------------------------------------------------

Omega_90 = calculate_omega_sensitivity(
    Omega_base,
    0.90
)


bl_90 = calculate_black_litterman(
    Pi,
    Sigma.values,
    P,
    Q,
    TAU,
    Omega_90
)

bl_90.name = "BL 90%"


# ============================================================
# 17. COMPARACIÓN DE RETORNOS
# ============================================================

print("\n")
print("=" * 70)
print("7. RETORNOS ESPERADOS")
print("=" * 70)


returns_table = pd.DataFrame({

    "Historical":
        historical_returns,

    "CAPM":
        capm_returns,

    "BL Base":
        bl_base,

    "BL 30%":
        bl_30,

    "BL 60%":
        bl_60,

    "BL 90%":
        bl_90

})


print("\n")

print(
    returns_table.to_string(
        float_format=lambda x:
        f"{x:.2%}"
    )
)


# ============================================================
# 18. FUNCIÓN DE OPTIMIZACIÓN
# ============================================================

def optimize_max_sharpe(
    expected_returns,
    covariance,
    risk_free
):

    n = len(expected_returns)


    def objective(weights):

        portfolio_return = (
            weights @ expected_returns
        )


        portfolio_volatility = np.sqrt(
            weights
            @ covariance
            @ weights
        )


        sharpe = (
            portfolio_return -
            risk_free
        ) / portfolio_volatility


        return -sharpe


    constraints = [
        {
            "type": "eq",
            "fun": lambda w:
            np.sum(w) - 1
        }
    ]


    bounds = [
        (0, MAX_WEIGHT)
        for _ in range(n)
    ]


    x0 = np.repeat(
        1 / n,
        n
    )


    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={
            "maxiter": 2000,
            "ftol": 1e-12
        }
    )


    if not result.success:

        print(
            "\nAdvertencia:",
            result.message
        )


    return result.x


# ============================================================
# 19. OPTIMIZACIÓN
# ============================================================

print("\n")
print("=" * 70)
print("8. OPTIMIZANDO PORTAFOLIOS")
print("=" * 70)


# CAPM

weights_capm = optimize_max_sharpe(
    capm_returns.values,
    Sigma.values,
    rf
)


# BL BASE

weights_bl_base = optimize_max_sharpe(
    bl_base.values,
    Sigma.values,
    rf
)


# Sensibilidad

weights_bl_30 = optimize_max_sharpe(
    bl_30.values,
    Sigma.values,
    rf
)


weights_bl_60 = optimize_max_sharpe(
    bl_60.values,
    Sigma.values,
    rf
)


weights_bl_90 = optimize_max_sharpe(
    bl_90.values,
    Sigma.values,
    rf
)


# ============================================================
# 20. PESOS
# ============================================================

print("\n")
print("=" * 70)
print("9. COMPOSICIÓN DE PORTAFOLIOS")
print("=" * 70)


weights_table = pd.DataFrame({

    "Benchmark":
        BENCHMARK_WEIGHTS,

    "CAPM":
        weights_capm,

    "BL Base":
        weights_bl_base,

    "BL 30%":
        weights_bl_30,

    "BL 60%":
        weights_bl_60,

    "BL 90%":
        weights_bl_90

}, index=TICKERS)


print("\n")

print(
    weights_table.to_string(
        float_format=lambda x:
        f"{x:.2%}"
    )
)


# ============================================================
# 21. MÉTRICAS
# ============================================================

def portfolio_metrics(
    weights,
    expected_returns,
    covariance,
    risk_free
):

    portfolio_return = (
        weights @ expected_returns
    )


    portfolio_volatility = np.sqrt(
        weights
        @ covariance
        @ weights
    )


    sharpe = (
        portfolio_return -
        risk_free
    ) / portfolio_volatility


    return {

        "Expected Return":
            portfolio_return,

        "Volatility":
            portfolio_volatility,

        "Sharpe Ratio":
            sharpe
    }


# CAPM

metrics_capm = portfolio_metrics(
    weights_capm,
    capm_returns.values,
    Sigma.values,
    rf
)


# BL BASE

metrics_bl_base = portfolio_metrics(
    weights_bl_base,
    bl_base.values,
    Sigma.values,
    rf
)


# Sensibilidad

metrics_bl_30 = portfolio_metrics(
    weights_bl_30,
    bl_30.values,
    Sigma.values,
    rf
)


metrics_bl_60 = portfolio_metrics(
    weights_bl_60,
    bl_60.values,
    Sigma.values,
    rf
)


metrics_bl_90 = portfolio_metrics(
    weights_bl_90,
    bl_90.values,
    Sigma.values,
    rf
)


# ============================================================
# 22. MÉTRICAS CAPM VS BL BASE
# ============================================================

print("\n")
print("=" * 70)
print("10. MÉTRICAS PRINCIPALES")
print("=" * 70)


main_metrics = pd.DataFrame({

    "CAPM":
        metrics_capm,

    "BL Base (60%)":
        metrics_bl_base,

    "BL 30%":
        metrics_bl_30,

    "BL 90%":
        metrics_bl_90

})


print("\n")

print(
    main_metrics.to_string(
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# 23. SENSIBILIDAD
# ============================================================

print("\n")
print("=" * 70)
print("11. SENSIBILIDAD BL")
print("=" * 70)


sensitivity_metrics = pd.DataFrame({

    "BL 30%":
        metrics_bl_30,

    "BL 60%":
        metrics_bl_60,

    "BL 90%":
        metrics_bl_90

})


print("\n")

print(
    sensitivity_metrics.to_string(
        float_format=lambda x:
        f"{x:.6f}"
    )
)


# ============================================================
# 24. FRONTERA EFICIENTE
# ============================================================

def efficient_frontier(
    expected_returns,
    covariance,
    n_points=50
):

    n = len(expected_returns)


    bounds = [
        (0, MAX_WEIGHT)
        for _ in range(n)
    ]


    sum_constraint = {
        "type": "eq",
        "fun": lambda w:
        np.sum(w) - 1
    }


    def portfolio_variance(weights):

        return (
            weights
            @ covariance
            @ weights
        )


    x0 = np.repeat(
        1 / n,
        n
    )


    # --------------------------------------------------------
    # Mínima varianza
    # --------------------------------------------------------

    min_var_result = minimize(

        portfolio_variance,

        x0,

        method="SLSQP",

        bounds=bounds,

        constraints=[sum_constraint],

        options={
            "maxiter": 2000,
            "ftol": 1e-12
        }
    )


    min_var_weights = (
        min_var_result.x
    )


    min_return = (
        min_var_weights
        @ expected_returns
    )


    # --------------------------------------------------------
    # Máximo retorno
    # --------------------------------------------------------

    max_return_result = minimize(

        lambda w:
        -(w @ expected_returns),

        x0,

        method="SLSQP",

        bounds=bounds,

        constraints=[sum_constraint],

        options={
            "maxiter": 2000,
            "ftol": 1e-12
        }
    )


    max_return = (
        max_return_result.x
        @ expected_returns
    )


    target_returns = np.linspace(
        min_return,
        max_return,
        n_points
    )


    frontier_volatility = []
    frontier_returns = []


    for target in target_returns:

        constraints = [

            sum_constraint,

            {
                "type": "eq",

                "fun":
                lambda w,
                target=target:

                w @ expected_returns -
                target
            }
        ]


        result = minimize(

            portfolio_variance,

            x0,

            method="SLSQP",

            bounds=bounds,

            constraints=constraints,

            options={
                "maxiter": 2000,
                "ftol": 1e-12
            }
        )


        if result.success:

            volatility = np.sqrt(
                portfolio_variance(
                    result.x
                )
            )


            frontier_volatility.append(
                volatility
            )


            frontier_returns.append(
                target
            )


    return (
        np.array(frontier_volatility),
        np.array(frontier_returns)
    )


# ============================================================
# 25. FRONTERAS CAPM VS BL BASE
# ============================================================

frontier_vol_capm, frontier_ret_capm = (
    efficient_frontier(
        capm_returns.values,
        Sigma.values
    )
)


# IMPORTANTE:
#
# La frontera utiliza BL BASE.
#
# NO utiliza BL 30, 60 o 90.

frontier_vol_bl, frontier_ret_bl = (
    efficient_frontier(
        bl_base.values,
        Sigma.values
    )
)


# ============================================================
# 26. PUNTOS DE MÁXIMO SHARPE
# ============================================================

capm_return = (
    weights_capm
    @ capm_returns.values
)


capm_volatility = np.sqrt(
    weights_capm
    @ Sigma.values
    @ weights_capm
)


bl_return = (
    weights_bl_base
    @ bl_base.values
)


bl_volatility = np.sqrt(
    weights_bl_base
    @ Sigma.values
    @ weights_bl_base
)


# ============================================================
# 27. GRÁFICA
# ============================================================

plt.figure(
    figsize=(14, 8)
)


plt.plot(
    frontier_vol_capm,
    frontier_ret_capm,
    label="Frontera CAPM",
    linewidth=2
)


plt.plot(
    frontier_vol_bl,
    frontier_ret_bl,
    label="Frontera Black-Litterman",
    linewidth=2
)


plt.scatter(
    capm_volatility,
    capm_return,
    s=180,
    label="Máximo Sharpe CAPM"
)


plt.scatter(
    bl_volatility,
    bl_return,
    s=180,
    label="Máximo Sharpe BL Base"
)


plt.xlabel(
    "Volatilidad anualizada"
)


plt.ylabel(
    "Retorno esperado"
)


plt.title(
    "Frontera eficiente: CAPM vs Black-Litterman"
)


plt.grid(
    True,
    alpha=0.3
)


plt.legend()


plt.tight_layout()


plt.show()


# ============================================================
# 28. RESUMEN
# ============================================================

print("\n")
print("=" * 70)
print("12. RESUMEN FINAL")
print("=" * 70)


print(
    f"\nUST 5Y: {rf:.2%}"
)

print(
    f"ERP Damodaran: {ERP_DAMODARAN:.2%}"
)

print(
    f"Tau: {TAU:.2f}"
)

print(
    f"Delta: {DELTA:.2f}"
)

print(
    "\nFrecuencia: MENSUAL"
)

print(
    "Inicio: enero de 2020"
)


print("\nCAPM")

print(
    f"Retorno: "
    f"{metrics_capm['Expected Return']:.2%}"
)

print(
    f"Volatilidad: "
    f"{metrics_capm['Volatility']:.2%}"
)

print(
    f"Sharpe: "
    f"{metrics_capm['Sharpe Ratio']:.4f}"
)


print("\nBLACK-LITTERMAN BASE")

print(
    f"Retorno: "
    f"{metrics_bl_base['Expected Return']:.2%}"
)

print(
    f"Volatilidad: "
    f"{metrics_bl_base['Volatility']:.2%}"
)

print(
    f"Sharpe: "
    f"{metrics_bl_base['Sharpe Ratio']:.4f}"
)


print("\n")
print("=" * 70)
print("FIN DEL PROGRAMA")
print("=" * 70)