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
    f1 : float  -->  Frecuencia inicial del barrido en Hz (predeterminado: 20 Hz).
    f2 : float  -->  Frecuencia final del barrido en Hz (predeterminado: 20000 Hz).
    duracion : float  -->  Duracion del barrido en segundos (predeterminado: 2 segundos).
    fs : int  -->  Frecuencia de muestreo en Hz (predeterminado: 48000 Hz).

    Returns
    -------
    sweep : np.ndarray  --> Senal del barrido senoidal.
    filtro_inverso : np.ndarray  --> Filtro inverso correspondiente.

    Referencias
    ----------
    .. [1] Farina, A. (2000). "Simultaneous measurement of impulse response and distortion with a swept-sine technique."
    """

    # Creamos un arreglo con  N = (duracion * fs) muestras, y armamos un arreglo con esa cantidad de muestras.
    # Luego, dividimos por la frecuencia de muestreo para obtener tiempos reales en lugar de muestras, y armar el vector tiempo.

    muestras = duracion * fs
    t = np.arange(int(muestras)) / fs

    # Construimos la fase del sine sweep senoidal a partir de la tecnia Farina.

    fase = (2 * np.pi * f1 * duracion / (np.log(f2 / f1))) * (np.exp((t / duracion) * (np.log(f2 / f1))) - 1)

    # Creamos el sine sweep a partir de dicha fase.

    sweep = np.sin(fase)

    # Ahora, para construir el filtro inverso, primero invertimos el arreglo del sine sweep en el tiempo usando la funcion de slicing

    sweep_invertido = sweep[::-1]

    # El sine sweep tiene mucha energía acumulada en los graves y poca en los agudos, por lo que queremos que el filtro inverso compense esta situacion.
    # Para ello, creamos una envolvente que depende del vector tiempo, la cual atenúa las frecuencias bajas y amplifica las altas.

    envolvente = (f2 / f1) ** -(t / (2 * duracion))

    # Finalmente multiplicamos la envolvente con el sine sweep invertido para obtener el filtro inverso.

    filtro_inverso = sweep_invertido * envolvente

    # La función creada devuelve tanto el sine sweep logarítmico como su filtro inverso. Ambos valores son arreglos.

    return sweep, filtro_inverso

