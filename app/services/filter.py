"""Servicio de filtrado por bandas de octava.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

import numpy as np
from scipy import signal


def filtro_octava(signal: np.ndarray, fc: float, fs: int, orden: int = 4) -> np.ndarray:
    
    """
    Acciones
    --------
    Aplica un filtro pasabanda de una octava centrado en ``fc``.

    Implementa un filtro Butterworth pasabanda cuyas frecuencias de corte
    corresponden a los limites de una banda de octava segun IEC 61260:
    - Frecuencia inferior: ``fc / sqrt(2)``
    - Frecuencia superior: ``fc * sqrt(2)``

    Parameters
    ----------
    signal: np.ndarray --> Senal de entrada (array 1D).
    fc: float --> Frecuencia central de la banda de octava en Hz.
    fs: int --> Frecuencia de muestreo en Hz.
    orden: int, optional --> Orden del filtro Butterworth (por defecto 4).

    Returns
    -------
    np.ndarray --> Senal filtrada (array 1D).
    """

    # Aseguramos que la frecuencia central entregada esté dentro de las normalizadas.

    frec_cent_normalizadas = np.array[31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

    # Calculamos cada una de las frecuencias de corte por cada frecuencia central normalizada.
    # Guardamos en un array a cada frecuencia de corte inferior y superior.

    f_inf = frec_cent_normalizadas/(np.sqrt(2))
    f_sup = frec_cent_normalizadas*(np.sqrt(2))

    # Calculamos la frecuencia de Nyquist

    f_nyquist = fs/2

    # Ahora dividimos cada una de las frecuencias de corte con la frecuencia de sampleo fs, para cumplir con el teorema de Nyquist

    w_inf = f_inf/f_nyquist
    w_sup = f_sup/f_nyquist

    #

    diccionario = {}

    # Calculamos los parámetros del filtro butterworth

    for (inferior, superior), f in zip(w_inf, w_sup), frec_cent_normalizadas:

        b, a = signal.butter(orden, [w_inf, w_sup], btype='band')

        signal_filtrada = signal.filtfilt(b, a, signal)

        diccionario[f in frec_cent_normalizadas].append(signal_filtrada)

    print(diccionario[0])

    return diccionario

