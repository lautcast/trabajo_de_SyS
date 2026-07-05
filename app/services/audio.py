import numpy as np
import sounddevice as sd
from pathlib import Path

def reproducir_y_grabar(signal: np.ndarray, fs: int, duracion_grabacion: float, pre_roll: float = 0.5) -> np.ndarray:
    """
    Reproduce una señal de excitación y graba simultáneamente la respuesta acústica,
    asegurando la captura de la cola de reverberación y añadiendo un tiempo de pre-roll.

    Parameters
    ----------
    signal : np.ndarray
        Vector 1D con la señal de excitación a reproducir (ej. sine sweep o ruido rosa).
    fs : int
        Frecuencia de muestreo en Hz.
    duracion_grabacion : float
        Duración total del bloque de grabación en segundos. Debe contemplar el pre-roll,
        la duración de la señal y la cola de decaimiento del recinto.
    pre_roll : float, opcional
        Tiempo de silencio previo a la reproducción en segundos para estabilizar 
        el transductor o medir ruido de fondo. Por defecto 0.5s.

    Returns
    -------
    np.ndarray
        Vector 1D con la señal de audio grabada (formato mono).
    """
    # 1. Validaciones de consistencia
    if signal.ndim > 1:
        raise ValueError("La señal de excitación debe ser un arreglo unidimensional (mono).")

    muestras_totales = int(duracion_grabacion * fs)
    muestras_pre_roll = int(pre_roll * fs)
    muestras_senal = len(signal)

    # Validar que el tiempo total solicitado cubra al menos el estímulo y el pre-roll
    if muestras_totales < (muestras_pre_roll + muestras_senal):
        duracion_minima = (muestras_pre_roll + muestras_senal) / fs
        raise ValueError(
            f"La 'duracion_grabacion' ({duracion_grabacion}s) es insuficiente. "
            f"Debe ser de al menos {duracion_minima:.2f}s para cubrir el pre-roll y la señal."
        )

    # 2. Construcción del buffer de salida (Zero-padding)
    # Rellenamos con ceros para mantener el canal en silencio durante el pre-roll y la reverberación
    signal_play = np.zeros(muestras_totales, dtype=np.float64)
    signal_play[muestras_pre_roll : muestras_pre_roll + muestras_senal] = signal

    # 3. Interacción sincrónica con hardware y manejo de excepciones de dispositivo
    try:
        grabacion = sd.playrec(
            signal_play,
            samplerate=fs,
            channels=1,
            blocking=True,
            dtype='float32'
        )
    except sd.PortAudioError as e:
        raise RuntimeError(
            f"Fallo de hardware de audio: No se detectaron dispositivos de entrada/salida válidos "
            f"o la configuración de hardware es incompatible. Detalles: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Error inesperado durante la ejecución de playrec: {e}")

    # 4. Post-procesamiento del resultado
    # Sounddevice devuelve una matriz (muestras x canales). Aplanamos a un vector 1D mono.
    return grabacion.flatten()