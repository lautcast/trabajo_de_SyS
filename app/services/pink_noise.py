"""Servicio de generacion de ruido rosa.

Milestone 1: Generacion de senales.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

def generar_ruido_rosa(duracion: float, fs: int) -> np.ndarray:
    """Genera una senal de ruido rosa de la duracion especificada.

    El ruido rosa tiene una densidad espectral de potencia inversamente
    proporcional a la frecuencia (1/f). Esto significa que cada octava
    contiene la misma cantidad de energia, lo cual lo hace util para
    mediciones acusticas.

    Parameters
    ----------
    duracion : float
        Duracion de la senal en segundos.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Senal de ruido rosa normalizada, de longitud ``int(duracion * fs)``.
    """
    # 1. Generar ruido blanco (distribución normal) de la duración deseada
    N = int(duracion * fs)
    ruido_blanco = np.random.randn(N)
    
    # 2. Aplicar la transformada de Fourier (np.fft.rfft)
    espectro = np.fft.rfft(ruido_blanco)
    
    # 3. Crear un vector de frecuencias correspondiente
    frecuencias = np.fft.rfftfreq(N, d=1/fs)
    
    # 4. Dividir cada componente por sqrt(f) (omitir f=0 para evitar división por cero)
    escala = np.ones_like(frecuencias)
    escala[1:] = 1.0 / np.sqrt(frecuencias[1:])
    espectro_escalado = espectro * escala
    
    # 5. Aplicar la transformada inversa (np.fft.irfft)
    # Se especifica n=N para garantizar que la longitud de salida sea exactamente la requerida
    ruido_rosa = np.fft.irfft(espectro_escalado, n=N)
    
    # 6. Normalizar la señal resultante al rango [-1, 1]
    max_abs = np.max(np.abs(ruido_rosa))
    if max_abs > 0:
        ruido_rosa = ruido_rosa / max_abs
        
    return ruido_rosa

if __name__ == '__main__':
    # Todo lo que esté acá adentro SOLO se ejecuta si corrés este archivo directamente
    fs = 48000  # Frecuencia de muestreo estándar de audio
    duracion = 10.0  # 2 segundos de prueba
    ruido = generar_ruido_rosa(duracion, fs)

    # --- 1. Verificación de Criterios de Aceptación ---
    print("Ejecutando pruebas de la Issue...")

    assert isinstance(ruido, np.ndarray), "Error: No es un np.ndarray"
    assert len(ruido) == int(duracion * fs), "Error: La longitud no coincide"
    assert np.max(np.abs(ruido)) <= 1.0, "Error: La señal no está en el rango [-1, 1]"
    assert not np.isnan(ruido).any(), "Error: Hay valores NaN (probable división por cero)"
    assert not np.isinf(ruido).any(), "Error: Hay valores infinitos"

    print("✅ Todos los criterios de aceptación técnicos pasaron con éxito.\n")

    # --- 2. Verificación Visual (Densidad Espectral) ---
    print("Generando gráfico de Densidad Espectral de Potencia...")

    # Welch es el método estándar para estimar la densidad espectral de potencia (PSD)
    frecuencias, psd = welch(ruido, fs, nperseg=8192)

    plt.figure(figsize=(10, 6))
    # Usamos loglog porque en una escala logarítmica, la curva 1/f se ve como una línea recta descendente
    plt.loglog(frecuencias, psd, label='Señal generada')

    # Dibujamos una línea teórica de 1/f para comparar
    frecuencias_teoricas = frecuencias[1:] # Evitamos el cero
    linea_teorica = psd[1] * (frecuencias_teoricas[0] / frecuencias_teoricas)
    plt.loglog(frecuencias_teoricas, linea_teorica, 'r--', label='Pendiente teórica 1/f', alpha=0.8)

    plt.title('Densidad Espectral de Potencia: Ruido Rosa')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Potencia')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
