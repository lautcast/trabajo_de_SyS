"Milestone 2 a 3: Endpoints de Filtrado"


import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from scipy import signal


def filtro_octava(signal_in: np.ndarray, fc: float, fs: int, orden: int = 4) -> np.ndarray:
    frec_cent_normalizadas = np.array([31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
    if fc not in frec_cent_normalizadas:
        raise ValueError(f"La frecuencia central especificada ({fc} Hz) no se encuentra dentro de la norma IEC 61260")

    f_inf = fc / (np.sqrt(2))
    f_sup = fc * (np.sqrt(2))
    f_nyquist = fs / 2

    w_inf = f_inf / f_nyquist
    w_sup = f_sup / f_nyquist

    sos = signal.butter(orden, [w_inf, w_sup], btype='band', output='sos')
    signal_filtrada = signal.sosfiltfilt(sos, signal_in)
    return signal_filtrada

class FilterBandRequest(BaseModel):
    # Field(...) permite agregar documentación que se verá en el Swagger UI
    signal_in: list[float] = Field(..., description="Arreglo de la señal de audio cruda")
    fc: float = Field(..., description="Frecuencia central de la banda de octava (Hz)")
    fs: int = Field(..., description="Frecuencia de muestreo (Hz)")
    orden: int = Field(4, description="Orden del filtro Butterworth")

class FilterBandResponse(BaseModel):
    signal_out: list[float] = Field(..., description="Arreglo de la señal de audio filtrada")

router = APIRouter(
    prefix="/api/v1/filters",
    tags=["Filters"]
)

@router.get("/frequencies")
def list_frequencies():
    """
    Lista frecuencias centrales:
    Devuelve las frecuencias centrales normalizadas según la norma IEC 61260.
    """
    frec_cent_normalizadas = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    return {"frecuencias_centrales_hz": frec_cent_normalizadas}

@router.post("/band", response_model=FilterBandResponse)
def filter_audio_by_band(request: FilterBandRequest):
    """
    Filtra audio por bandas de octava:
    Recibe una señal cruda en formato JSON, le aplica un filtro IIR Butterworth 
    centrado en 'fc' y devuelve la señal procesada.
    """
    # 1. Transformar JSON web (List) a matemática pura (NumPy Array)
    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # 2. Llamar a tu función
        senal_filtrada = filtro_octava(
            signal_in=senal_numpy,
            fc=request.fc,
            fs=request.fs,
            orden=request.orden
        )

        # 3. Transformar matemática pura (NumPy Array) de vuelta a JSON (List)
        return FilterBandResponse(signal_out=senal_filtrada.tolist())

    except ValueError as e:
        # Si el usuario mandó una frecuencia inválida, atrapamos TU error y devolvemos un Bad Request (400)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Cualquier otro error matemático inesperado
        raise HTTPException(status_code=500, detail=f"Error interno en el filtrado: {str(e)}")
