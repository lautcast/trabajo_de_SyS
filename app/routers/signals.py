"Milestone 1 a 3: Endpoints de Generación"

from fastapi import APIRouter, Query, Body
from typing import List
from app.services.pink_noise import generar_ruido_rosa
import io
import numpy as np
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from scipy.io import wavfile

from app.services.pink_noise import generar_ruido_rosa
from app.services.sine_sweep import generar_sine_sweep
from app.services.signal_utils import sintetizar_ri

router = APIRouter()

# router.get para la funcion generar_ruido_rosa.

@router.get("/pink-noise", summary="Generar y descargar Ruido Rosa")
def get_pink_noise(
    duracion: float = Query(2.0, gt=0, le=10.0, description="Duración en segundos"),
    fs: int = Query(44100, gt=0, description="Frecuencia de muestreo en Hz")
):
    """
    Genera ruido rosa y lo devuelve como un archivo de audio .wav descargable.
    """

    # Generamos la señal usando la función de generar_ruido_rosa, importada desde la carpeta services
    
    ruido = generar_ruido_rosa(duracion, fs)

    # Convertimos de float64 [-1, 1] a PCM 16-bit (estándar para archivos WAV)
    # Esto es necesario para que el reproductor de audio entienda la amplitud.

    audio_int16 = (ruido * 32767).astype(np.int16)

    # Crear un buffer de memoria (archivo virtual)
    
    buffer = io.BytesIO()
    
    # Escribimos el audio del buffer en formato WAV
    
    wavfile.write(buffer, fs, audio_int16)
    
    # Volvemos al inicio del buffer para que FastAPI pueda leerlo desde el principio
    
    buffer.seek(0)

    # Devolver el flujo de datos con el tipo de medio correcto
    
    return StreamingResponse(buffer, media_type="audio/wav",headers={"Content-Disposition": f"attachment; filename=ruido_rosa_{duracion}s.wav"})


# router.get para la funcion generar_sine_sweep.


@router.get("/sine-sweep", summary="Generar y descargar Sine Sweep Logarítmico")
def get_sine_sweep(
    f1: float = Query(20.0, gt=0, description="Frecuencia inicial en Hz."),
    f2: float = Query(20000.0, gt=0, description="Frecuencia final en Hz."),
    duracion: float = Query(2.0, gt=0, le=30.0, description="Duración en segundos."),
    fs: int = Query(48000, gt=0, description="Frecuencia de muestreo en Hz.")
):
    
    """
     Genera un sine sweep logarítmico y lo devuelve como archivo .wav descargable.
    
    """

    # Generamos la señal usando la función (descartamos el filtro inverso para la descarga)

    sine_sweep, filto_inv = generar_sine_sweep(f1=f1, f2=f2, duracion=duracion, fs=fs)

    # Convertimos los datos del arreglo a PCM 16-bit.
    # Multiplicamos por 32767 para normalizar el float [-1, 1] al rango de int16
    
    audio_int16 = (sine_sweep * 32767).astype(np.int16)

    # Creamos un buffer de memoria

    buffer = io.BytesIO()

    # Escribimos el audio en el buffer en formato WAV
    
    wavfile.write(buffer, fs, audio_int16)

    # Volvemos al inicio del buffer
    
    buffer.seek(0)

    # Devolvemos el flujo de datos

    filename = f"sine_sweep-{int(f1)}_Hz_a_{int(f2)}_Hz-{duracion}_seg.wav"
    
    return StreamingResponse(buffer, media_type="audio/wav", headers={"Content-Disposition": f"attachment; filename={filename}"})
    

# router.get para la funcion sintetizar_ri.


@router.post("/siintetizar_ri", summary="Generar y descargar la Respuesta al Impulso de un recinto")
def get_sintetizar_ri(
    t60_por_banda: dict[float, float] = Body({31.5: 2, 63: 2, 125 : 2, 250: 2, 500: 2, 1000: 2, 2000: 2, 4000: 2, 8000: 2, 16000: 2}, gt=0, description="Lista con Claves:Valor tal que: [frecuencia central : T60 de la banda de octava]."),
    fs: int = Query(48000.0, gt=0, description="Frecuencia de muestreo en Hz."),
    duracion: float = Query(2.0, gt=0, le=30.0, description="Duración en segundos."),
):
    
    """
        Genera una respuesta al impulso de un recinto    
    """

    # Generamos la señal usando la función (descartamos el filtro inverso para la descarga)

    ri = sintetizar_ri(t60_por_banda = t60_por_banda, fs = fs, duracion=duracion)

    # Convertimos los datos del arreglo a PCM 16-bit.
    # Multiplicamos por 32767 para normalizar el float [-1, 1] al rango de int16
    
    audio_int16 = (ri * 32767).astype(np.int16)

    # Creamos un buffer de memoria

    buffer = io.BytesIO()

    # Escribimos el audio en el buffer en formato WAV
    
    wavfile.write(buffer, fs, audio_int16)

    # Volvemos al inicio del buffer
    
    buffer.seek(0)

    # Devolvemos el flujo de datos

    filename = f"RI_sintetizado-{fs}_Hz-{duracion}_seg.wav"
    
    return StreamingResponse(buffer, media_type="audio/wav", headers={"Content-Disposition": f"attachment; filename={filename}"})
    
