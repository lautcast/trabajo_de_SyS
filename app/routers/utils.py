"Milestone 3: Endpoints de utilidades"

from fastapi import APIRouter, Query, Body
from typing import List
from app.services.pink_noise import generar_ruido_rosa
import io
import numpy as np
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from scipy.io import wavfile

from app.services.signal_utils import sintetizar_ri


router = APIRouter()

# router.get para la funcion sintetizar_ri.

@router.post("/siintetizar_ri", summary="Generar y descargar la Respuesta al Impulso de un recinto")
def get_sintetizar_ri(
    t60_por_banda: dict[float, float] = Body({31.5: 2, 63: 2, 125 : 2, 250: 2, 500: 2, 1000: 2, 2000: 2, 4000: 2, 8000: 2, 16000: 2}, description="Lista con Claves:Valor tal que: [frecuencia central : T60 de la banda de octava]."),
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
    
    audio_float = np.asarray(ri, dtype=np.float32)
    
    # Creamos un buffer de memoria

    buffer = io.BytesIO()

    # Escribimos el audio en el buffer en formato WAV
    
    wavfile.write(buffer, fs, audio_float)

    # Volvemos al inicio del buffer
    
    buffer.seek(0)

    # Devolvemos el flujo de datos

    filename = f"RI_sintetizado-{fs}_Hz-{duracion}_seg.wav"
    
    return StreamingResponse(buffer, media_type="audio/wav", headers={"Content-Disposition": f"attachment; filename={filename}"})