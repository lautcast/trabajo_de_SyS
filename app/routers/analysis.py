import os
import tempfile
from pathlib import Path

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.acoustic_parameters import calcular_parametros_acusticos
from app.services.signal_utils import cargar_audio


# Nota: Ya no necesitamos AnalysisRequest porque ahora entra un archivo directamente
class AnalysisResponse(BaseModel):
    mensaje: str = Field(..., description="Estado del análisis")
    frecuencia_muestreo: int
    parametros_por_banda: dict[str, dict[str, float | None]]



router = APIRouter()

@router.post("/impulse-response", response_model=AnalysisResponse, summary="Análisis de RI (Carga de Archivo WAV)")
async def analyze_impulse_response_file(file: UploadFile = File(...)):
    """
    Endpoint Maestro para el Demo Day:
    Permite subir un archivo de audio (.wav o .flac) directamente. 
    Internamente lo carga, lo convierte a mono (si es estéreo), 
    y calcula todos los parámetros acústicos ISO 3382.
    """
    # 1. Validamos que el archivo tenga nombre y revisamos su extensión
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un nombre de archivo válido.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ['.wav', '.flac']:
        raise HTTPException(status_code=400, detail="El archivo debe ser .wav o .flac")

    # 2. Guardamos el archivo subido en un archivo TEMPORAL seguro
    # Esto es obligatorio porque tu función 'cargar_audio' pide una 'ruta' en el disco duro.
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_audio:
            # Leemos los bytes que manda el navegador y los escribimos en disco
            contenido = await file.read()
            temp_audio.write(contenido)
            ruta_temporal = temp_audio.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando el archivo temporal: {e}") from e

    try:
        # 3. Usamos TU función cargar_audio pasándole la ruta del archivo temporal
        senal_numpy, fs = cargar_audio(ruta=ruta_temporal)

        # 4. Si el archivo es estéreo (o multicanal), lo pasamos a mono para la matemática
        if senal_numpy.ndim > 1:
            senal_numpy = np.mean(senal_numpy, axis=1)

        # 5. Ejecutamos tu motor matemático
        resultados_acusticos = calcular_parametros_acusticos(ri=senal_numpy, fs=fs)

        # 6. Formateamos las claves a texto para que el JSON no explote (como vimos antes)
        resultados_formateados = {}
        for parametro, valores in resultados_acusticos.items():
            resultados_formateados[parametro] = {str(frec): val for frec, val in valores.items()}

        # 7. Devolvemos el resultado triunfal
        return AnalysisResponse(
            mensaje="Análisis acústico completado con éxito.",
            frecuencia_muestreo=fs,
            parametros_por_banda=resultados_formateados
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en el motor de análisis: {str(e)}") from e

    finally:
        # 8. LIMPIEZA: Siempre borramos el archivo temporal para no llenar la compu de basura
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
