"""Servicio de generacion de sine sweep logaritmico.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generar_sine_sweep(f1: float = 20.00, f2: float = 20000.00, duracion: float = 2, fs: int = 48000) -> tuple[np.ndarray, np.ndarray]:
    """
    Acciones
    --------
    La funcion genera un barrido senoidal logaritmico (sine sweep) y su filtro inverso.

    Definiciones
    ------------
    El sine sweep logaritmico es la senal de excitacion preferida para la medicion de respuestas al impulso segun la tecnica de Farina (2000).

    Parametros
    ----------
    f1 : float  -->  Frecuencia inicial del barrido en Hz (tipicamente 20 Hz).
    f2 : float  -->  Frecuencia final del barrido en Hz (tipicamente 20000 Hz).
    duracion : float  -->  Duracion del barrido en segundos.
    fs : int  -->  Frecuencia de muestreo en Hz.

    Returns
    -------
    sweep : np.ndarray  --> Senal del barrido senoidal.
    filtro_inverso : np.ndarray  --> Filtro inverso correspondiente.

    Referencias
    ----------
    .. [1] Farina, A. (2000). "Simultaneous measurement of impulse response and distortion with a swept-sine technique."
    """

    # Creamos un arreglo con  N = (duracion * fs) muestras.
    # Dividimos por fs para obtener tiempos reales en lugar de muestras.
    t = np.arange(int(duracion * fs)) / fs

    # Construimos la fase 
    fase = (2 * np.pi * f1 * duracion / (np.log(f2 / f1))) * (np.exp((t / duracion) * (np.log(f2 / f1))) - 1)
    
    sweep = np.sin(fase)

    # 3. Construir el filtro inverso
    # Invertimos el arreglo del sweep en el tiempo usando slicing
    sweep_invertido = sweep[::-1]

    # Creamos la envolvente de atenuación para "blanquear" el espectro del filtro
    envolvente = (f2 / f1) ** -(t / duracion)
    
    filtro_inverso = sweep_invertido * envolvente

    return sweep, filtro_inverso

