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

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import numpy as np
import io
from scipy.io import wavfile

# Asumo que tu router ya está definido arriba
# router = APIRouter()

# 1. Definimos el modelo de datos que el usuario enviará en el body del POST
class SintetizarRIRequest(BaseModel):
    # Opcion 1: Requerido, sin los tres puntos, y usando json_schema_extra para el ejemplo
    t60_por_banda: dict[float, float] = Field(
        description="Diccionario de frecuencias centrales (Hz) y su T60 (segundos)",
        json_schema_extra={
            "example": {
                "125.0": 2.0, 
                "250.0": 1.8, 
                "500.0": 1.5, 
                "1000.0": 1.2, 
                "2000.0": 1.0, 
                "4000.0": 0.8
            }
        }
    )
    fs: int = Field(default=44100, gt=0, description="Frecuencia de muestreo en Hz")
    duracion: float = Field(default=2.0, gt=0, le=10.0, description="Duración total en segundos")


# 2. El endpoint POST
@router.post("/sintetizar-ri", summary="Sintetizar y descargar Respuesta al Impulso (RI)")
def post_sintetizar_ri(request: SintetizarRIRequest):
    """
    Sintetiza una respuesta al impulso estocástica basada en T60 por bandas y la devuelve como un archivo de audio .wav descargable.
    """

    # Generamos la señal usando la función de sintetizar_ri, importada desde la carpeta services
    # Le pasamos los parámetros que vienen en el body (request)
    ri_flotante = sintetizar_ri(request.t60_por_banda, request.fs, request.duracion)

    # Convertimos de float64 [-1, 1] a PCM 16-bit (estándar para archivos WAV)
    # Esto es necesario para que el reproductor de audio entienda la amplitud.
    audio_int16 = (ri_flotante * 32767).astype(np.int16)

    # Crear un buffer de memoria (archivo virtual)
    buffer = io.BytesIO()
    
    # Escribimos el audio del buffer en formato WAV
    wavfile.write(buffer, request.fs, audio_int16)
    
    # Volvemos al inicio del buffer para que FastAPI pueda leerlo desde el principio
    buffer.seek(0)

    # Devolver el flujo de datos con el tipo de medio correcto
    return StreamingResponse(
        buffer, 
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename=ri_sintetizada_{request.duracion}s.wav"}
    )