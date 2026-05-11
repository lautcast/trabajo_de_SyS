"Milestone 1 a 3: Endpoints de Generación"

from fastapi import APIRouter, Query
from typing import List
from app.services.pink_noise import generar_ruido_rosa
import io
import numpy as np
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from scipy.io import wavfile

from app.services.pink_noise import generar_ruido_rosa


router = APIRouter()

@router.get("/pink-noise", summary="Generar y descargar Ruido Rosa")
def get_pink_noise(
    duracion: float = Query(2.0, gt=0, le=10.0, description="Duración en segundos"),
    fs: int = Query(44100, gt=0, description="Frecuencia de muestreo en Hz")
):
    """
    Genera ruido rosa y lo devuelve como un archivo de audio .wav descargable.
    """
    # 1. Generar la señal usando tu función existente
    ruido = generar_ruido_rosa(duracion, fs)

    # 2. Convertir de float64 [-1, 1] a PCM 16-bit (estándar para archivos WAV)
    # Esto es necesario para que el reproductor de audio entienda la amplitud.
    audio_int16 = (ruido * 32767).astype(np.int16)

    # 3. Crear un buffer de memoria (archivo virtual)
    buffer = io.BytesIO()
    
    # 4. Escribir el audio en el buffer en formato WAV
    wavfile.write(buffer, fs, audio_int16)
    
    # 5. Volver al inicio del buffer para que FastAPI pueda leerlo desde el principio
    buffer.seek(0)

    # 6. Devolver el flujo de datos con el tipo de medio correcto
    return StreamingResponse(
        buffer, 
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename=ruido_rosa_{duracion}s.wav"}
    )