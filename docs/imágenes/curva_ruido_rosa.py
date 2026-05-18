import sys
from pathlib import Path
ruta_raiz = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ruta_raiz))
from app.services.pink_noise import generar_ruido_rosa

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

"""

El objetivo de este código es verificar gráficamente que el ruido rosa cae 3 dB por octava.

"""

# Utilizamos la funcion generar_ruido_rosa

duracion = 2.0
fs = 48000

ruido_rosa = generar_ruido_rosa(duracion, fs)

# Aplicamos el Método de Welch

frecuencias, psd = signal.welch(ruido_rosa, fs, nperseg=8192)

# Convertimos toda la PSD a decibeles

psd_db = 10 * np.log10(psd)

# Elegimos dos frecuencias estándar de audio a una octava de distancia

f1 = 1000.0  # 1 kHz
f2 = 2000.0  # 2 kHz

# Buscamos los índices más cercanos a estas frecuencias en nuestro array

idx1 = np.argmin(np.abs(frecuencias - f1))
idx2 = np.argmin(np.abs(frecuencias - f2))

# Extraemos los valores en dB

db1 = psd_db[idx1]
db2 = psd_db[idx2]

# Calculamos la diferencia

caida_db = db2 - db1

print("\n--- RESULTADOS DE LA VERIFICACION ---")
print(f"Potencia a {frecuencias[idx1]:.1f} Hz:  {db1:.2f} dB")
print(f"Potencia a {frecuencias[idx2]:.1f} Hz:  {db2:.2f} dB")
print(f"Caida medida: {caida_db:.2f} dB por octava")
print("Caida teorica esperada: -3.01 dB")
print("-------------------------------------\n")

# Graficamos

plt.figure(figsize=(10, 6))
plt.loglog(frecuencias, psd, color='magenta', label='Ruido Rosa')

ref_frecuencias = frecuencias[1:]
ref_linea = psd[1] * (ref_frecuencias[0] / ref_frecuencias)
plt.loglog(ref_frecuencias, ref_linea, 'k--', label='Referencia ideal 1/f')

# Podemos marcar los puntos que analizamos en el gráfico

plt.plot([frecuencias[idx1], frecuencias[idx2]], [psd[idx1], psd[idx2]], 'ko', markersize=8, label='Puntos de medición (1kHz y 2kHz)')

plt.title('Verificación de Ruido Rosa (Espectro de Potencia)')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Densidad de Potencia')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()
plt.show()