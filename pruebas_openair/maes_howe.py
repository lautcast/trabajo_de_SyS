import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Le indicamos a Python dónde encontrar tu módulo 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Asegurate de que las rutas de importación coincidan con tu estructura
from app.services.signal_utils import cargar_audio, a_escala_log
from app.services.filter import filtro_octava

# ==========================================
# 1. CARGA DEL ARCHIVO .WAV
# ==========================================
# Cambiá el string por la ruta exacta donde guardaste tu RI de OpenAIR
ruta_openair = r"C:\Users\12cas\OneDrive\Desktop\OPENAIR\mh3_000_ortf_48k.wav" 

print(f"Cargando audio desde: {ruta_openair}")
datos = cargar_audio(ruta_openair)

# Extraemos la señal y la frecuencia de muestreo del diccionario que armaste
ri_cruda = datos[0]
fs = datos[1]

# ¡LA LÍNEA SALVADORA! 
# Si la señal tiene más de 1 dimensión (es estéreo), nos quedamos solo con la primera columna (canal izquierdo)
if ri_cruda.ndim > 1:
    ri_cruda = ri_cruda[:, 0]

# ==========================================
# 2. APLICACIÓN DEL FILTRO DE OCTAVA
# ==========================================
frecuencia_central = 1000.0  # Podés cambiar esto para probar otras bandas
orden = 4

ri_filtrada = filtro_octava(ri_cruda, frecuencia_central, fs, orden)

# ==========================================
# 3. GRÁFICO 1: DOMINIO DEL TIEMPO (Amplitud Lineal)
# ==========================================
# Creamos el vector de tiempo en segundos
total_muestras = len(ri_cruda)
tiempo = np.linspace(0.0, total_muestras / fs, total_muestras, endpoint=False, dtype=np.float64)

plt.figure(figsize=(12, 5))
# Graficamos la original de fondo clarito y la filtrada por encima
plt.plot(tiempo, ri_cruda, color='#005088', label='RI Original (Banda Ancha)', alpha=0.7, linewidth=1)

plt.title('Respuesta al Impulso en el Dominio del Tiempo (Amplitud Lineal)', fontsize=14, fontweight='bold')
plt.xlabel('Tiempo (segundos)', fontsize=12)
plt.ylabel('Amplitud', fontsize=12)
plt.axhline(0, color='black', linewidth=0.8, alpha=0.5)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# ==========================================
# 4. GRÁFICO 2: DOMINIO DE LA FRECUENCIA (Espectro)
# ==========================================
# Usamos el método de Welch para obtener una curva espectral limpia de la Respuesta al Impulso
# nperseg=8192 nos da una excelente resolución en frecuencias graves
frecuencias, psd_cruda = signal.welch(ri_cruda, fs, nperseg=8192)
_, psd_filtrada = signal.welch(ri_filtrada, fs, nperseg=8192)

# Convertimos la energía a escala logarítmica (dB) manualmente para poder graficar 
# el espectro correctamente sin depender de tu módulo externo.
psd_cruda_db = 10 * np.log10(np.maximum(psd_cruda, 1e-12))
psd_filtrada_db = 10 * np.log10(np.maximum(psd_filtrada, 1e-12))

plt.figure(figsize=(12, 5))
# Graficamos usando semilogx para que el eje X (Hz) se vea como en los ecualizadores
plt.semilogx(frecuencias, psd_cruda_db, color='lightgray', label='Espectro Original')
plt.semilogx(frecuencias, psd_filtrada_db, color='#11CAA0', label=f'Espectro Filtrado ({frecuencia_central} Hz)', linewidth=2)

# Marcamos las frecuencias de corte teóricas del filtro
f_inf = frecuencia_central / np.sqrt(2)
f_sup = frecuencia_central * np.sqrt(2)
plt.axvline(f_inf, color='red', linestyle='--', alpha=0.7, label=f'Corte Inferior ({f_inf:.1f} Hz)')
plt.axvline(f_sup, color='red', linestyle='--', alpha=0.7, label=f'Corte Superior ({f_sup:.1f} Hz)')

plt.title('Espectro Frecuencial: Acción del Filtro Butterworth', fontsize=14, fontweight='bold')
plt.xlabel('Frecuencia (Hz) [Escala Logarítmica]', fontsize=12)
plt.ylabel('Densidad de Potencia (dB)', fontsize=12)
plt.xlim([20, 20000])  # Limitamos la vista al rango de audición humana
plt.ylim([-120, np.max(psd_cruda_db) + 10])
plt.legend(loc='lower center')
plt.grid(True, which="both", linestyle='--', alpha=0.3)
plt.tight_layout()

# ==========================================
# 5. MOSTRAR AMBAS VENTANAS
# ==========================================
plt.show()