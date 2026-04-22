# SyS_2026
Trabajo para la materia señales y sistemas.

# RIR-API

API REST desarrollada en Python utilizando FastAPI para el cálculo de parámetros acústicos a partir de respuestas al impulso (RIR), siguiendo la norma ISO 3382.

El sistema permite generar señales de excitación, procesar respuestas al impulso y calcular parámetros como RT60, C50 y EDT. La API está diseñada para ser consumida por clientes externos como aplicaciones web, scripts o herramientas de análisis.

---

## 🎯 Objetivo técnico

Procesar respuestas al impulso (RIR) y calcular parámetros acústicos según la norma ISO 3382.

---

## 👥 Integrantes

- Pellegrino Salvador - Legajo: 75978 - Rol: Backend / API
- Castrillo Lautaro - Legajo: 70558 - Rol: Procesamiento de señales
- Maiolo Ivan - Legajo: 76593 - Rol: Testing / Documentación

---

## 🛠️ Tecnologías

- FastAPI
- NumPy
- SciPy
- Pydantic
- Uvicorn
- Matplotlib
- Soundfile
- Sounddevice
- Python-multipart

---

## ⚙️ Instalación

### Clonar el repositorio

```bash
git clone https://github.com/salvipellegrino/SyS_2026.git
cd SyS_2026
```


### Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate
```


### Instalar dependencias
```bash
pip install -r requirements.txt
```


### Ejecutar la api:
```bash
uvicorn app.main:app --reload
```


### 🌐 Acceso a la API
Una vez ejecutada:
Documentación interactiva: http://127.0.0.1:8000/docs
Estado del servidor: http://127.0.0.1:8000/health


### Estructura del proyecto
```bash
app/
├── main.py          # Punto de entrada
├── routers/         # Endpoints
├── services/        # Lógica (vacío por ahora)
├── schemas/         # Validación (vacío por ahora)
```


### Estrategia de ramas
**Main** -> rama protegida
**Feature/nombre** -> nuevas funcionalidades



### Convencion de commits
- **feat**: nueva funcionalidad
- **fix**: corrección de errores

---