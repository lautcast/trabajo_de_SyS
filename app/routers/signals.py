"""Milestone 1 a 3: Endpoints de Generación y Filtrado"""

import io
import os
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from scipy.io import wavfile

# Importaciones de tus servicios
from app.services.pink_noise import generar_ruido_rosa
from app.services.sine_sweep import generar_sine_sweep
# Asegurate de importar cargar_audio y filtro_octava
from app.services.signal_utils import sintetizar_ri, cargar_audio
from app.services.acoustic_parameters import filtro_octava

router = APIRouter()

"""-----------------------------------------------------------------------------------------------------"""
# MODELOS PYDANTIC
"""-----------------------------------------------------------------------------------------------------"""

class PinkNoiseRequest(BaseModel):
    duracion: float = Field(2.0, gt=0, le=10.0, description="Duración en segundos")
    fs: int = Field(44100, gt=0, description="Frecuencia de muestreo en Hz")

class SineSweepRequest(BaseModel):
    f1: float = Field(20.0, gt=0, description="Frecuencia inicial en Hz.")
    f2: float = Field(20000.0, gt=0, description="Frecuencia final en Hz.")
    duracion: float = Field(2.0, gt=0, le=30.0, description="Duración en segundos.")
    fs: int = Field(48000, gt=0, description="Frecuencia de muestreo en Hz.")

class SintetizarRIRequest(BaseModel):
    t60_por_banda: dict[float, float] = Field(
        description="Diccionario de frecuencias centrales (Hz) y su T60 (segundos)",
        json_schema_extra={
            "example": {
                "125.0": 2.0,
                "250.0": 1.8,
                "500.0": 1.5,
                "1000.0": 1.2,
                "2000.0": 1.0,
                "4000.0": 0.8,
            }
        },
    )
    fs: int = Field(default=44100, gt=0, description="Frecuencia de muestreo en Hz")
    duracion: float = Field(default=2.0, gt=0, le=10.0, description="Duración total en segundos")


"""-----------------------------------------------------------------------------------------------------"""
# ENDPOINTS ORIGINALES (Generación)
"""-----------------------------------------------------------------------------------------------------"""

@router.post("/pink-noise", summary="Generar y descargar Ruido Rosa")
def post_pink_noise(request: PinkNoiseRequest):
    """
    Genera ruido rosa y lo devuelve como un archivo de audio .wav descargable.
    """
    ruido = generar_ruido_rosa(request.duracion, request.fs)
    audio_int16 = (ruido * 32767).astype(np.int16)

    buffer = io.BytesIO()
    wavfile.write(buffer, request.fs, audio_int16)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename=ruido_rosa_{request.duracion}s.wav"}
    )

@router.post("/sine-sweep", summary="Generar y descargar Sine Sweep Logarítmico")
def post_sine_sweep(request: SineSweepRequest):
    """
    Genera un sine sweep logarítmico y lo devuelve como archivo .wav descargable.
    """
    sine_sweep, filto_inv = generar_sine_sweep(
        f1=request.f1,
        f2=request.f2,
        duracion=request.duracion,
        fs=request.fs
    )
    audio_int16 = (sine_sweep * 32767).astype(np.int16)

    buffer = io.BytesIO()
    wavfile.write(buffer, request.fs, audio_int16)
    buffer.seek(0)

    filename = f"sine_sweep-{int(request.f1)}_Hz_a_{int(request.f2)}_Hz-{request.duracion}_seg.wav"

    return StreamingResponse(
        buffer,
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/sintetizar-ri", summary="Sintetizar y descargar Respuesta al Impulso (RI)")
def post_sintetizar_ri(request: SintetizarRIRequest):
    """
    Sintetiza una respuesta al impulso estocástica basada en T60 por bandas y la devuelve como un archivo de audio .wav descargable.
    """
    ri_flotante = sintetizar_ri(request.t60_por_banda, request.fs, request.duracion)
    audio_int16 = (ri_flotante * 32767).astype(np.int16)

    buffer = io.BytesIO()
    wavfile.write(buffer, request.fs, audio_int16)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename=ri_sintetizada_{request.duracion}s.wav"
        },
    )

"""-----------------------------------------------------------------------------------------------------"""
# NUEVO ENDPOINT (Filtrado y Escucha)
"""-----------------------------------------------------------------------------------------------------"""

@router.post("/filter/listen", summary="Filtrar Audio y Escuchar (Banda de Octava)")
async def filter_and_listen_audio(
    file: UploadFile = File(...),
    fc: float = Form(..., description="Frecuencia central de la banda de octava (ej: 1000, 500, 250)")
):
    """
    Sube un archivo de audio, lo filtra en la banda de octava especificada
    y devuelve un archivo .wav listo para ser escuchado o descargado.
    """
    if not file.filename:
        raise HTTPException(status_code=422, detail="Archivo inválido.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ['.wav', '.flac']:
        raise HTTPException(status_code=422, detail="Solo se permiten .wav o .flac")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_audio:
            temp_audio.write(await file.read())
            ruta_temporal = temp_audio.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando el archivo: {e}") from e

    try:
        senal_numpy, fs = cargar_audio(ruta=ruta_temporal)
        
        if senal_numpy.ndim > 1:
            senal_numpy = np.mean(senal_numpy, axis=1)

        audio_filtrado = filtro_octava(senal_numpy, fc=fc, fs=fs, orden=4)

        buffer = io.BytesIO()
        sf.write(buffer, audio_filtrado, fs, format='WAV', subtype='PCM_16')
        buffer.seek(0)

        nombre_salida = f"audio_filtrado_{int(fc)}Hz.wav"
        
        return StreamingResponse(
            buffer, 
            media_type="audio/wav", 
            headers={"Content-Disposition": f'attachment; filename="{nombre_salida}"'}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en el filtrado: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)