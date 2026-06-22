"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Analisis de parametros acusticos.
"""

import numpy as np
from scipy import signal

def suavizar_signal(signal: np.ndarray, ventana: int | str = 'hilbert') -> np.ndarray:
    """Aplica un suavizado por media movil a la senal.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (array 1D).
    ventana : int
        Tamano de la ventana de suavizado en muestras.

    Returns
    -------
    np.ndarray
        Senal suavizada, de la misma longitud que ``signal``.
    """

    # Opción A: Media Móvil

    if isinstance(ventana, int) and ventana > 0:

        # Trabajamos con la energía (amplitud al cuadrado)
        energia = signal ** 2
        
        # Creamos el kernel para el promedio
        kernel = np.ones(ventana) / ventana
        
        # Aplicamos la convolución para deslizar la ventana rápidamente
        # mode='same' asegura que el arreglo de salida tenga el mismo tamaño que la entrada
        senal_suavizada = np.convolve(energia, kernel, mode='same')

        return senal_suavizada

    # Opción B: Envolvente de Hilbert

    elif ventana == 'hilbert':
        
        analitica = signal.hilbert(signal)
        envolvente = np.abs(analitica)
        
        # Hilbert devuelve amplitud. Si los pasos posteriores requieren estrictamente energía, puedes devolver envolvente**2
        
        return envolvente
        
    else:
        raise ValueError("El parámetro 'ventana' debe ser 'hilbert' o un entero positivo.")


def integral_schroeder(ri: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve).

    Parameters
    ----------
    ri : np.ndarray
        Respuesta al impulso (array 1D).

    Returns
    -------
    np.ndarray
        Curva de decaimiento energetico (EDC), normalizada.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." The Journal of the Acoustical Society of America.
    """
    raise NotImplementedError("Implementar en Milestone 3")


def regresion_lineal(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Calcula la regresion lineal por minimos cuadrados.

    Parameters
    ----------
    x : np.ndarray
        Variable independiente (array 1D).
    y : np.ndarray
        Variable dependiente (array 1D).

    Returns
    -------
    pendiente : float
        Pendiente de la recta ajustada (m).
    ordenada : float
        Ordenada al origen de la recta ajustada (b).
    """
    raise NotImplementedError("Implementar en Milestone 3")


def calcular_parametros_acusticos(ri: np.ndarray, fs: int) -> dict[str, dict[float, float]]:
    """Calcula los parametros acusticos de una sala a partir de su RI.

    Parameters
    ----------
    ri : np.ndarray --> Respuesta al impulso (array 1D).
    fs : int --> Frecuencia de muestreo en Hz.

    Returns
    -------
    dict -->Diccionario con los parametros acusticos por banda.

    References
    ----------
    [1] ISO 3382-1:2009. "Acoustics -- Measurement of room acoustic parameters -- Part 1: Performance spaces."
    """
    raise NotImplementedError("Implementar en Milestone 3")


def metodo_lundeby(ri: np.ndarray, fs: int) -> int:
    """Estima el punto de truncamiento de la RI (metodo de Lundeby).

    Parameters
    ----------
    ri : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    int
        Indice de la muestra donde se estima el punto de truncamiento.

    Notes
    -----
    Esta funcion es **opcional** (extra credit).

    References
    ----------
    .. [1] Lundeby, A. et al. (1995). "Uncertainties of measurements in
       room acoustics." Acta Acustica.
    """
    raise NotImplementedError("Implementar en Milestone 3 (opcional)")

#prueba