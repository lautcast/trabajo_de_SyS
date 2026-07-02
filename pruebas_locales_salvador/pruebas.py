import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------
# 1. TUS FUNCIONES (Copiadas tal cual las definimos)
# ---------------------------------------------------------
def integral_schroeder(ri: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve)."""
    energia = ri ** 2
    edc = np.cumsum(energia[::-1])[::-1]
    edc_normalizada = edc / np.max(edc)
    return edc_normalizada

def regresion_lineal(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Calcula la regresion lineal por minimos cuadrados."""
    coeficientes = np.polyfit(x, y, 1)
    pendiente = float(coeficientes[0])
    ordenada = float(coeficientes[1])
    return pendiente, ordenada

# ---------------------------------------------------------
# 2. BLOQUE DE PRUEBA (Se ejecuta si corres este script)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Iniciando prueba acústica local...")

    # --- A. Generar señal de prueba (RI simulada) ---
    fs = 48000
    duracion = 2.0  # segundos
    t = np.arange(int(fs * duracion)) / fs

    # Creamos ruido y le aplicamos un decaimiento para que simule una sala.
    # Matemática rápida: con un alfa de 6.9, el T60 teórico debería dar alrededor de 1.0 segundo.
    ruido = np.random.randn(len(t))
    decaimiento = np.exp(-6.9 * t)
    ri_prueba = ruido * decaimiento

    # --- B. Procesamiento: Integral de Schroeder ---
    edc_lineal = integral_schroeder(ri_prueba)

    # Pasamos a decibeles (sumamos un valor ínfimo 1e-12 para evitar hacer logaritmo de cero)
    edc_db = 10 * np.log10(edc_lineal + 1e-12)

    # --- C. Recortar segmento para ISO 3382 (T20: de -5dB a -25dB) ---
    # Buscamos los índices de tiempo donde la curva pasa por -5 y -25
    idx_inicio = np.argmin(np.abs(edc_db - (-5)))
    idx_fin = np.argmin(np.abs(edc_db - (-25)))

    x_recorte = t[idx_inicio:idx_fin]
    y_recorte = edc_db[idx_inicio:idx_fin]

    # --- D. Aplicar tu Regresión Lineal ---
    pendiente, ordenada = regresion_lineal(x_recorte, y_recorte)

    # El T60 es el tiempo que tarda en caer 60 dB
    t60_calculado = -60 / pendiente
    print(f"-> Pendiente calculada: {pendiente:.2f} dB/s")
    print(f"-> T60 Resultante (basado en T20): {t60_calculado:.3f} segundos")

    # --- E. Graficar resultados ---
    plt.figure(figsize=(10, 6))
    plt.plot(t, edc_db, label="Curva de Schroeder (EDC)", color='#38bdf8')

    # Graficamos la recta de regresión extendida un poco para que se vea bien
    y_recta = pendiente * x_recorte + ordenada
    plt.plot(x_recorte, y_recta, label=f"Regresión Lineal (T60={t60_calculado:.2f}s)", color='red', linewidth=3)

    # Decoración del gráfico
    plt.axhline(-5, color='gray', linestyle='--', alpha=0.5, label='Límite -5 dB')
    plt.axhline(-25, color='gray', linestyle='--', alpha=0.5, label='Límite -25 dB')
    plt.ylim(-60, 5)
    plt.xlim(0, 1.5)
    plt.title("Prueba: Integral de Schroeder y Regresión Lineal")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Nivel (dB)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    print("Abriendo gráfico...")
    plt.show()
