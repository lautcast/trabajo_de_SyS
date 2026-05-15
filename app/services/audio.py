import numpy as np
import sounddevice as sd

def reproducir_y_grabar(senal_salida: np.ndarray, fs: int, canales_entrada: int = 1) -> np.ndarray:
    """
    Reproduce una señal de excitación por los altavoces locales y graba 
    simultáneamente la respuesta acústica usando el micrófono local.

    Al interactuar directamente con el hardware, esta función está diseñada 
    para uso local/laboratorio y no debe ser expuesta a través de un endpoint HTTP.

    Parameters
    ----------
    senal_salida : np.ndarray
        Vector con la señal a reproducir (ej. ruido rosa o sine sweep).
    fs : int
        Frecuencia de muestreo en Hz.
    canales_entrada : int, opcional
        Cantidad de canales a grabar (1 para mono, 2 para estéreo). Por defecto 1.

    Returns
    -------
    np.ndarray
        Vector con la señal de audio grabada por el micrófono.
    """
    # playrec reproduce y graba al mismo tiempo de forma sincrónica.
    grabacion = sd.playrec(
        senal_salida, 
        samplerate=fs, 
        channels=canales_entrada, 
        blocking=True  # hace que Python espere a que termine el audio
    )
    
    # sounddevice devuelve una matriz 2D (muestras x canales). 
    # Si es mono (1 canal), la aplanamos a un vector 1D para que sea más fácil 
    # procesarla después con SciPy o NumPy.
    if canales_entrada == 1:
        grabacion = grabacion.flatten()
        
    return grabacion