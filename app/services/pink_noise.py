"""Servicio de generacion de ruido rosa.

Milestone 1: Generacion de senales.
"""

import numpy as np


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

    # Generamos un ruido blanco de la duración deseada

    n = int(duracion * fs)
    ruido_blanco = np.random.randn(n)

    # Aplicar la transformada de Fourier a través de la funcion (np.fft.rfft)

    t_fourier = np.fft.rfft(ruido_blanco)

    # Creamos un vector de frecuencias correspondiente.

    frecuencias = np.fft.rfftfreq(n, d=1/fs)

    # Dividimos cada componente por sqrt(f) (omitir f=0 para evitar división por cero)

    escala = np.ones_like(frecuencias)
    escala[1:] = 1.0 / np.sqrt(frecuencias[1:])
    espectro_escalado = t_fourier * escala

    # Aplicamos la transformada inversa (np.fft.irfft)
    # Se especifica n=N para garantizar que la longitud de salida sea exactamente la requerida
    ruido_rosa = np.fft.irfft(espectro_escalado, n = n)

    # Normalizamos la señal resultante al rango [-1, 1]
    max_abs = np.max(np.abs(ruido_rosa))
    if max_abs > 0:
        ruido_rosa = ruido_rosa / max_abs

    return ruido_rosa


