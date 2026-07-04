"""Tests para los endpoints de la API (Milestone 3)."""

import numpy as np
import scipy.io.wavfile as wavfile
from fastapi.testclient import TestClient
import io

from app.main import app

client = TestClient(app)

"-------------------------------------------------------------------------------------------------------"

class TestAPIEndpointsyHealthCheck:
    """Tests para los endpoints de FastAPI."""

    def test_health_check(self):
        """Verifica que el endpoint de salud esté operativo."""
        client = TestClient(app) # (O borrá esta línea si ya definiste 'client' arriba de todo)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_analysis_endpoint(self):
        """Enviar un archivo WAV a /api/v1/analysis/impulse-response y verificar respuesta."""
        client = TestClient(app)

        #Fabricamos un archivo WAV en la memoria RAM para no tener que crear archivos reales en el disco
        fs = 44100
        duracion = 1.0
        t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)
        ri_falsa = np.random.randn(len(t)).astype(np.float32)

        buffer = io.BytesIO()
        wavfile.write(buffer, fs, ri_falsa)
        buffer.seek(0) # Volvemos al inicio del archivo virtual

        #Se simula la subida (Upload) del archivo como form-data
        response = client.post(
        "/api/v1/analysis/impulse-response",
        files={"file": ("test_ri.wav", buffer, "audio/wav")}
        )

         #Verificamos que la API lo haya procesado y devuelto un 200 OK
        assert response.status_code == 200
         #Verificamos que devuelva los parámetros, por ejemplo, el C80.
        assert "C80" in response.json()["parametros_por_banda"]

    def test_signals_pink_noise_endpoint(self):
         """Verificar que /api/v1/signals/pink-noise genera y devuelve un WAV valido."""
         client = TestClient(app)
         response = client.post("/api/v1/signals/pink-noise", json={"duracion": 1.0,"fs": 44100})

         #Verificamos que el pedido fue exitoso
         assert response.status_code == 200

         # Verificamos que el servidor nos está devolviendo un archivo de audio y no un texto
         assert response.headers["content-type"] == "audio/wav"

    def test_invalid_file_returns_422(self):
         """Verificar que un archivo invalido retorna 422 Unprocessable Entity."""
         client = TestClient(app)

         #Fabricamos un archivo de texto cualquiera, simulando que el usuario se equivocó
         archivo_falso = io.BytesIO(b"Este es un archivo de texto, no un audio.")

         #Se lo mandamos al endpoint que procesa audios
         response = client.post(
         "/api/v1/analysis/impulse-response",
         files={"file": ("documento.txt", archivo_falso, "text/plain")}
         )

         #Verificamos que la API se haya defendido correctamente tirando un 422, "Unprocessable Entity"
         assert response.status_code == 422
