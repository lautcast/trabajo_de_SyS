import os
import tempfile
from pathlib import Path
import numpy as np

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

# Importaciones de tus servicios
from app.services.acoustic_parameters import calcular_parametros_acusticos, calcular_parametros_globales, metodo_lundeby
from app.services.signal_utils import cargar_audio
from app.services.filter import filtro_octava

router = APIRouter()

# ==========================================
# 1. MODELOS DE RESPUESTA PYDANTIC
# ==========================================

class LundebyResult(BaseModel):
    muestra_truncamiento: int = Field(..., description="Índice de la muestra de truncamiento")
    tiempo_segundos: float = Field(..., description="Tiempo exacto de truncamiento en segundos")
    nivel_ruido_db: float = Field(..., description="Nivel de ruido de fondo estimado en dB")

class AcousticsBroadbandResponse(BaseModel):
    EDT: float | None = Field(None, description="Early Decay Time global (segundos)")
    T10: float | None = Field(None, description="T10 global (segundos)")
    T20: float | None = Field(None, description="T20 global (segundos)")
    T30: float | None = Field(None, description="T30 global (segundos)")
    D50: float | None = Field(None, description="Definición global (%)")
    C80: float | None = Field(None, description="Claridad global (dB)")
    Lundeby: LundebyResult | None = Field(None, description="Resultados del análisis de Lundeby global")

class AcousticsByBandsResponse(BaseModel):
    EDT: dict[str, float | None]
    T10: dict[str, float | None]
    T20: dict[str, float | None]
    T30: dict[str, float | None]
    D50: dict[str, float | None]
    C80: dict[str, float | None]
    Lundeby: dict[str, LundebyResult] = Field(default_factory=dict, description="Resultados de Lundeby por banda de frecuencia")

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

frecuencias_octava = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

@router.post("/parameters/global", response_model=AcousticsBroadbandResponse, summary="Calcular Parámetros y Lundeby Global")
async def calcular_parametros_global_endpoint(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (.wav o .flac).
    Calcula los parámetros y el punto de truncamiento (Lundeby) para la señal completa.
    """
    senal_numpy, fs, ruta_temporal = await procesar_audio_subido(file)

    try:
        # 1. Análisis de parámetros globales
        resultados_globales = calcular_parametros_globales(ri=senal_numpy, fs=fs)
        
        # 2. Análisis de Lundeby global
        trunc_sample, noise_level = metodo_lundeby(senal_numpy, fs)
        lundeby_data = LundebyResult(
            muestra_truncamiento=trunc_sample,
            tiempo_segundos=round(trunc_sample / fs, 4),
            nivel_ruido_db=round(noise_level, 2)
        )
        
        # Combinamos y enviamos según el modelo
        return AcousticsBroadbandResponse(**resultados_globales, Lundeby=lundeby_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros globales: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)


@router.post("/parameters/by-bands", response_model=AcousticsByBandsResponse, summary="Calcular Parámetros y Lundeby por Bandas")
async def calcular_parametros_bandas_endpoint(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (.wav o .flac).
    La API lo filtra en bandas de octava y devuelve los parámetros y resultados de Lundeby por frecuencia.
    """
    senal_numpy, fs, ruta_temporal = await procesar_audio_subido(file)

    try:
        # 1. Análisis de parámetros acústicos por bandas
        resultados_acusticos = calcular_parametros_acusticos(ri=senal_numpy, fs=fs)
        
        resultados_formateados = {}
        for parametro, valores in resultados_acusticos.items():
            resultados_formateados[parametro] = {str(frec): val for frec, val in valores.items()}

        # 2. Análisis de Lundeby iterando por el banco de filtros
        f_nyquist = fs / 2
        lundeby_por_banda = {}
        
        for fc in frecuencias_octava:
            if (fc / np.sqrt(2)) >= f_nyquist:
                continue
                
            ri_filtrada = filtro_octava(senal_numpy, fc, fs)
            trunc_sample, noise_level = metodo_lundeby(ri_filtrada, fs)
            
            # Se usa el str(fc) como clave para que coincida con las claves de los otros parámetros en el JSON
            clave_banda = str(fc) if fc % 1 != 0 else str(int(fc))
            
            lundeby_por_banda[clave_banda] = LundebyResult(
                muestra_truncamiento=trunc_sample,
                tiempo_segundos=round(trunc_sample / fs, 4),
                nivel_ruido_db=round(noise_level, 2)
            )
            
        resultados_formateados["Lundeby"] = lundeby_por_banda

        return resultados_formateados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros acústicos por bandas: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
