"""Milestone 1 a 3: Endpoints de Generación y Filtrado"""

import io

import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from scipy.io import wavfile

# Importaciones de tus servicios
from app.services.pink_noise import generar_ruido_rosa
from app.services.sine_sweep import generar_sine_sweep
# Asegurate de importar cargar_audio y filtro_octava
from app.services.signal_utils import sintetizar_ri

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
