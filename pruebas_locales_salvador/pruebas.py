import matplotlib.pyplot as plt
import numpy as np
"""

# ---------------------------------------------------------
# 1. TUS FUNCIONES (Copiadas tal cual las definimos)
# ---------------------------------------------------------
def integral_schroeder(ri: np.ndarray) -> np.ndarray:
    Calcula la integral de Schroeder (Energy Decay Curve).
    energia = ri ** 2
    edc = np.cumsum(energia[::-1])[::-1]
    edc_normalizada = edc / np.max(edc)
    return edc_normalizada

def regresion_lineal(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    Calcula la regresion lineal por minimos cuadrados.
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
"""

import requests
import numpy as np
import time
import matplotlib.pyplot as plt

print("1. Generando RI sintética para prueba...")
fs = 48000
t = np.arange(fs * 2) / fs # 2 segundos de audio
ruido = np.random.randn(len(t))
decaimiento = np.exp(-3 * t) 
ri_sintetica = ruido * decaimiento

print("2. Preparando envío a la API...")
payload = {
    "ri": ri_sintetica.tolist(),
    "fs": fs
}

url = "http://127.0.0.1:8000/api/v1/analysis/impulse-response"

print("3. Enviando petición POST a la API (esto puede tardar unos segundos)...")
inicio = time.time()
respuesta = requests.post(url, json=payload)
fin = time.time()

print(f"\n--- RESPUESTA DEL SERVIDOR (Tardó {fin-inicio:.2f} segundos) ---")
if respuesta.status_code == 200:
    datos = respuesta.json()
    print("Estado:", datos["mensaje"])
    
    # --- GRÁFICO DE RESULTADOS ---
    # Extraemos específicamente el diccionario de T20
    t20_dict = datos["parametros_por_banda"]["T20"]
    
    # Separamos las claves (frecuencias) y los valores (segundos)
    bandas_hz = list(t20_dict.keys())
    valores_t20 = list(t20_dict.values())
    
    print("\nAbriendo gráfico del T20...")
    
    plt.figure(figsize=(10, 6))
    
    # Trazamos la línea con marcadores (estilo clásico de acústica)
    plt.plot(bandas_hz, valores_t20, marker='o', linestyle='-', color='#38bdf8', linewidth=2.5, markersize=8)
    
    # Decoramos el gráfico
    plt.title("Tiempo de Reverberación (T20) por Bandas de Octava", fontsize=14, fontweight='bold')
    plt.xlabel("Frecuencia Central (Hz)", fontsize=12)
    plt.ylabel("T20 (Segundos)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Damos un pequeño margen en el eje Y para que no quede pegado al techo
    plt.ylim(0, max(valores_t20) + 1.0)
    
    plt.show()

else:
    print(f"ERROR HTTP {respuesta.status_code}:")
    print(respuesta.text)