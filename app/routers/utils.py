"Milestone 3: Endpoints de utilidades"

import io

import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from scipy.io import wavfile

from app.services.signal_utils import a_escala_log, cargar_audio, sintetizar_ri

router = APIRouter()

# router.get para la funcion sintetizar_ri.

from fastapi import APIRouter

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
                "4000.0": 0.8,
            }
        },
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
        headers={
            "Content-Disposition": f"attachment; filename=ri_sintetizada_{request.duracion}s.wav"
        },
    )


import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

# router = APIRouter()


@router.post("/cargar-audio", summary="Subir y analizar archivo de audio")
async def post_cargar_audio(
    archivo: UploadFile = File(..., description="Archivo de audio (.wav o .flac)"),
):
    """
    Recibe un archivo de audio del usuario, lo carga usando la función interna y devuelve su información (metadata).
    """

    # 1. Validar la extensión rápidamente antes de guardar nada
    # Usamos 'or ""' para asegurarnos de que Path siempre reciba un string, nunca un None.
    nombre_archivo = archivo.filename or ""
    extension = Path(nombre_archivo).suffix.lower()

    if extension not in [".wav", ".flac"]:
        raise HTTPException(
            status_code=400, detail="Formato no soportado. Solo se admiten .wav y .flac."
        )

    # 2. Crear un archivo temporal en el servidor para guardar el audio subido
    # Usamos delete=False para que no se borre antes de que sf.read termine de leerlo
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
        ruta_temporal = tmp_file.name
        # Copiamos el contenido del archivo subido al archivo temporal en el disco
        shutil.copyfileobj(archivo.file, tmp_file)

    try:
        # 3. Llamamos a TU función exacta, pasándole la ruta del archivo que acabamos de guardar
        senal, fs = cargar_audio(ruta_temporal)

        # 4. Extraemos información útil para devolverle al usuario
        # Verificamos si es mono (1D) o estéreo/multicanal (2D)
        if senal.ndim == 1:
            canales = 1
            muestras = senal.shape[0]
        else:
            canales = senal.shape[1]
            muestras = senal.shape[0]

        duracion_segundos = muestras / fs

        # 5. Armamos la respuesta exitosa
        return {
            "status": "success",
            "message": "Audio cargado y analizado correctamente",
            "data": {
                "nombre_original": archivo.filename,
                "frecuencia_muestreo": fs,
                "canales": canales,
                "total_muestras": muestras,
                "duracion_segundos": round(duracion_segundos, 3),
                "forma_arreglo": senal.shape,
            },
        }

    except ValueError as e:
        # Si tu función lanza un ValueError (ej. archivo corrupto), devolvemos Error 400
        raise HTTPException(status_code=400, detail=str(e))

    except FileNotFoundError:
        # Si por alguna razón falla la ruta
        raise HTTPException(status_code=500, detail="Error interno al manejar el archivo temporal.")

    finally:
        # 6. LIMPIEZA: Siempre borramos el archivo temporal para no llenar el disco del servidor
        # Esto se ejecuta sin importar si hubo un error o fue un éxito
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)


from pydantic import BaseModel, Field


#  MODELOS DE DATOS (PYDANTIC)
class LogScaleRequest(BaseModel):
    signal_in: list[float] = Field(
        ..., description="Arreglo de la señal de audio lineal (amplitud)"
    )


class LogScaleResponse(BaseModel):
    signal_out: list[float] = Field(
        ..., description="Arreglo de la señal convertida a escala logarítmica (dB)"
    )


# ROUTER (Endpoint de Utils)

router = APIRouter(prefix="/api/v1/utils", tags=["Utils"])


@router.post("/log-scale", response_model=LogScaleResponse)
def convert_to_log_scale(request: LogScaleRequest):
    """
    Conversión a Escala Logarítmica:
    Recibe una señal de audio en valores lineales, calcula su valor absoluto,
    la normaliza al máximo y la convierte a decibeles (dB) aplicando un piso
    de ruido de -120 dB.
    """
    # 1. Transformar JSON web (List) a matemática pura (NumPy Array)
    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # 2. Ejecutar tu función
        senal_db = a_escala_log(signal=senal_numpy)

        # 3. Devolver el resultado transformado a lista estándar
        return LogScaleResponse(signal_out=senal_db.tolist())

    except Exception as e:
        # Por si ocurre algún error matemático imprevisto
        raise HTTPException(status_code=500, detail=f"Error en la conversión a dB: {str(e)}")
