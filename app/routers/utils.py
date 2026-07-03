"Milestone 3: Endpoints de utilidades"


import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.acoustic_parameters import integral_schroeder, suavizar_signal
from app.services.signal_utils import a_escala_log, cargar_audio

router = APIRouter()

# router.get para la funcion sintetizar_ri.

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




#  MODELOS DE DATOS (PYDANTIC)
class LogScaleRequest(BaseModel):
    signal_in: list[float] = Field(
        ..., description="Arreglo de la señal de audio lineal (amplitud)"
    )


class LogScaleResponse(BaseModel):
    signal_out: list[float] = Field(
        ..., description="Arreglo de la señal convertida a escala logarítmica (dB)"
    )


@router.post("/log-scale", response_model=LogScaleResponse)
def convertir_a_escala_logartimica(request: LogScaleRequest):
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

class SmoothingRequest(BaseModel):
    signal_in: list[float] = Field(..., description="Arreglo de la señal de entrada (array 1D)")
    ventana: int | str = Field(
        "hilbert", description="Tamaño de la ventana (entero positivo) o 'hilbert'"
    )
class SmoothingResponse(BaseModel):
    signal_out: list[float] = Field(..., description="Arreglo de la señal suavizada")


class SchroederRequest(BaseModel):
    ri: list[float] = Field(..., description="Arreglo de la Respuesta al Impulso (array 1D)")

class SchroederResponse(BaseModel):
    edc_db: list[float] = Field(..., description="Curva de decaimiento energético en dB (EDC)")

@router.post("/smoothing", response_model=SmoothingResponse, summary="Suavizar Señal")
def procesar_suavizado(request: SmoothingRequest):
    """
    Suavizado de Señal:
    Aplica un suavizado por media móvil (indicando una ventana entera positiva)
    o extrae la envolvente analítica utilizando la transformada de Hilbert.
    """
    # 1. Transformamos JSON a NumPy
    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # 2. Ejecutamos tu función matemática
        senal_suavizada = suavizar_signal(signal=senal_numpy, ventana=request.ventana)

        # 3. Devolvemos la respuesta
        return SmoothingResponse(signal_out=senal_suavizada.tolist())

    except ValueError as e:
        # Este except agarra exactamente el ValueError que escribiste al final de tu función
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Para cualquier otro error matemático no previsto
        raise HTTPException(status_code=500, detail=f"Error inesperado en el suavizado: {str(e)}")

@router.post("/schroeder", response_model=SchroederResponse, summary="Calcular Integral de Schroeder")
def procesar_schroeder(request: SchroederRequest):
    """
    Integral de Schroeder:
    Calcula la curva de decaimiento de energía (EDC) a partir de una 
    respuesta al impulso. Devuelve la curva ya normalizada y en escala 
    logarítmica (dB).
    """
    # 1. Transformamos JSON a NumPy
    senal_numpy = np.array(request.ri, dtype=np.float64)

    try:
        # 2. Ejecutamos tu función
        edc_resultado = integral_schroeder(ri=senal_numpy)

        # 3. Devolvemos la respuesta
        return SchroederResponse(edc_db=edc_resultado.tolist())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular la integral de Schroeder: {str(e)}")

