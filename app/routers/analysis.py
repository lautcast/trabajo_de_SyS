import os
import tempfile
from pathlib import Path

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

# Importaciones de tus servicios
from app.services.acoustic_parameters import calcular_parametros_acusticos, calcular_parametros_globales
from app.services.signal_utils import cargar_audio
from app.services.filter import filtro_octava

router = APIRouter()

# ==========================================
# 1. MODELOS DE RESPUESTA PYDANTIC
# ==========================================

class AcousticsByBandsResponse(BaseModel):
    EDT: dict[str, float | None]
    T10: dict[str, float | None]
    T20: dict[str, float | None]
    T30: dict[str, float | None]
    D50: dict[str, float | None]
    C80: dict[str, float | None]

class AcousticsBroadbandResponse(BaseModel):
    EDT: float | None = Field(None, description="Early Decay Time global (segundos)")
    T10: float | None = Field(None, description="T10 global (segundos)")
    T20: float | None = Field(None, description="T20 global (segundos)")
    T30: float | None = Field(None, description="T30 global (segundos)")
    D50: float | None = Field(None, description="Definición global (%)")
    C80: float | None = Field(None, description="Claridad global (dB)")

# ==========================================
# 2. FUNCIÓN AUXILIAR (Manejo de Archivos)
# ==========================================

async def procesar_audio_subido(file: UploadFile) -> tuple[np.ndarray, int, str]:
    """Guarda el archivo temporalmente, lo carga a mono y devuelve (señal, fs, ruta)."""
    if not file.filename:
        raise HTTPException(status_code=422, detail="No se proporcionó un nombre de archivo válido.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ['.wav', '.flac']:
        raise HTTPException(status_code=422, detail="El archivo debe ser .wav o .flac")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_audio:
            contenido = await file.read()
            temp_audio.write(contenido)
            ruta_temporal = temp_audio.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando el archivo temporal: {e}") from e

    try:
        senal_numpy, fs = cargar_audio(ruta=ruta_temporal)
        if senal_numpy.ndim > 1:
            senal_numpy = np.mean(senal_numpy, axis=1)
        return senal_numpy, fs, ruta_temporal
    except ValueError as e:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
        raise HTTPException(status_code=500, detail=f"Fallo al cargar audio: {str(e)}") from e


# ==========================================
# 3. ENDPOINTS PRINCIPALES
# ==========================================

@router.post("/parameters/by-bands", response_model=AcousticsByBandsResponse, summary="Calcular Parámetros por Bandas (Sube WAV)")
async def calcular_parametros_bandas_endpoint(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (.wav o .flac).
    La API lo filtra en bandas de octava y devuelve los parámetros (EDT, T20, etc.) por frecuencia.
    """
    senal_numpy, fs, ruta_temporal = await procesar_audio_subido(file)

    try:
        resultados_acusticos = calcular_parametros_acusticos(ri=senal_numpy, fs=fs)
        
        # Formateo a strings para que el JSON sea válido
        resultados_formateados = {}
        for parametro, valores in resultados_acusticos.items():
            resultados_formateados[parametro] = {str(frec): val for frec, val in valores.items()}

        return resultados_formateados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros acústicos: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)


@router.post("/parameters/global", response_model=AcousticsBroadbandResponse, summary="Calcular Parámetros Globales (Sube WAV)")
async def calcular_parametros_global_endpoint(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (.wav o .flac).
    La API calcula los parámetros para la señal completa sin aplicar filtrado.
    """
    senal_numpy, fs, ruta_temporal = await procesar_audio_subido(file)

    try:
        resultados_globales = calcular_parametros_globales(ri=senal_numpy, fs=fs)
        return AcousticsBroadbandResponse(**resultados_globales)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros globales: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
    

from app.services.acoustic_parameters import metodo_lundeby
import soundfile as sf
import io

# Importamos tu función (ajustá la ruta según la estructura de tu proyecto)
# from utils.acoustics import metodo_lundeby 

@router.post("/lundeby")
async def calcular_lundeby(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (WAV, FLAC) con una Respuesta al Impulso (RI)
    y devuelve el punto de truncamiento y el nivel de ruido de fondo.
    """
    # 1. Validación básica de formato
    # 1. Validación básica de formato
    filename = file.filename or "" # Si es None, lo convierte en un string vacío
    if not filename.lower().endswith(('.wav', '.flac')):
        raise HTTPException(status_code=400, detail="Formato no soportado. Por favor subí un archivo .wav o .flac")
    
    try:
        # 2. Leer el archivo directamente desde la memoria
        contenido = await file.read()
        
        # soundfile puede leer desde un objeto de bytes usando io.BytesIO
        ri, fs = sf.read(io.BytesIO(contenido))
        
        # 3. Acondicionamiento de la señal
        # Si el audio es estéreo (2D array), lo pasamos a mono tomando el canal izquierdo
        if len(ri.shape) > 1:
            ri = ri[:, 0] 
            
        # 4. Procesamiento con tu método
        trunc_sample, noise_level = metodo_lundeby(ri, fs)
        
        # Opcional: Calcular el tiempo en segundos para mayor utilidad en el frontend
        trunc_time_sec = trunc_sample / fs
        
        # 5. Respuesta de la API
        return {
            "archivo": file.filename,
            "frecuencia_muestreo": fs,
            "resultados_lundeby": {
                "muestra_truncamiento": trunc_sample,
                "tiempo_truncamiento_segundos": round(trunc_time_sec, 4),
                "nivel_ruido_dB": round(noise_level, 2)
            }
        }
        
    except Exception as e:
        # Capturamos cualquier error de lectura de audio o del algoritmo
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo de audio: {str(e)}")
    
from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np
import soundfile as sf
import io
from scipy import signal  # Requerido por tu función filtro_octava

# Importamos tu método Lundeby (ajustá la ruta según tu proyecto)
# from utils.acoustics import metodo_lundeby 


# Definimos las frecuencias de octava que analiza la API basadas en tu array
FRECUENCIAS_OCTAVA = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

@router.post("/lundeby-bandas")
async def calcular_lundeby_bandas(file: UploadFile = File(...)):
    # 1. Validación de formato
    filename = file.filename or ""
    if not filename.lower().endswith(('.wav', '.flac')):
        raise HTTPException(status_code=400, detail="Formato no soportado. Subí un archivo .wav o .flac")
    
    try:
        # 2. Leer archivo de audio
        contenido = await file.read()
        ri, fs = sf.read(io.BytesIO(contenido))
        
        # Monofónico por seguridad
        if len(ri.shape) > 1:
            ri = ri[:, 0] 
            
        f_nyquist = fs / 2
        resultados_por_banda = {}
        
        # 3. Iteración por bandas usando tu filtro
        for fc in FRECUENCIAS_OCTAVA:
            # Control de seguridad: Si la frecuencia inferior de la banda supera Nyquist, 
            # no se puede procesar en este archivo de audio (ej: analizar 16kHz en un audio de 8kHz)
            if (fc / np.sqrt(2)) >= f_nyquist:
                continue
                
            # Aplicamos tu filtro
            ri_filtrada = filtro_octava(ri, fc, fs)
            
            # Aplicamos Lundeby a la señal filtrada
            trunc_sample, noise_level = metodo_lundeby(ri_filtrada, fs)
            trunc_time_sec = trunc_sample / fs
            
            # Formateamos la clave para el JSON (ej: "500Hz" o "31.5Hz")
            clave_banda = f"{fc}Hz" if fc % 1 == 0 else f"{fc}Hz"
            
            resultados_por_banda[clave_banda] = {
                "muestra_truncamiento": trunc_sample,
                "tiempo_segundos": round(trunc_time_sec, 4),
                "nivel_ruido_dB": round(noise_level, 2)
            }
            
        return {
            "archivo": filename,
            "frecuencia_muestreo": fs,
            "analisis_lundeby": resultados_por_banda
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")