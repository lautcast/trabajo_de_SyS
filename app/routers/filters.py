"""Endpoints de Filtrado"""

import numpy as np
import io
import os
import tempfile
import soundfile as sf
from pathlib import Path
from fastapi.responses import StreamingResponse
from app.services.filter import filtro_octava
from app.services.signal_utils import cargar_audio
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field


router = APIRouter()

"""-----------------------------------------------------------------------------------------------------"""

class FilterBandRequest(BaseModel):
    # Field(...) permite agregar documentación que se verá en el Swagger UI
    signal_in: list[float] = Field(..., description="Arreglo de la señal de audio cruda")
    fc: float = Field(..., description="Frecuencia central de la banda de octava (Hz)")
    fs: int = Field(..., description="Frecuencia de muestreo (Hz)")
    orden: int = Field(4, description="Orden del filtro Butterworth")


class FilterBandResponse(BaseModel):
    signal_out: list[float] = Field(..., description="Arreglo de la señal de audio filtrada")

"""-----------------------------------------------------------------------------------------------------"""

# Router para la función lista_de_frecuencias_centrales.

@router.get("/frequencies")
def lista_de_frecuencias_centrales():
    """
    Lista frecuencias centrales:
    Devuelve las frecuencias centrales normalizadas según la norma IEC 61260.
    """
    frec_cent_normalizadas = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    return {"frecuencias_centrales_hz": frec_cent_normalizadas}


"""-----------------------------------------------------------------------------------------------------"""

# Router para la función filtro_octava.

@router.post("/band", response_model=FilterBandResponse)
def filtrar_audio_por_banda(request: FilterBandRequest):
    """
    Filtra audio por bandas de octava:
    Recibe una señal cruda en formato JSON, le aplica un filtro IIR Butterworth
    centrado en 'fc' y devuelve la señal procesada.
    """

    # Transformar JSON web (List) a matemática pura (NumPy Array)

    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # Llamamos a filtro_octava

        senal_filtrada = filtro_octava(signal_in=senal_numpy, fc=request.fc, fs=request.fs, orden=request.orden)

        # Transformamos la  matemática pura (NumPy Array) de vuelta a JSON (List)

        return FilterBandResponse(signal_out=senal_filtrada.tolist())

    except ValueError as e:

        # Si el usuario mandó una frecuencia inválida, tomamos el error y se devuelve un Bad Request (400).

        raise HTTPException(status_code=400, detail=str(e)) from e
    
    except Exception as e:

        # Cualquier otro error matemático inesperado.

        raise HTTPException(status_code=500, detail=f"Error interno en el filtrado: {str(e)}") from e


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
