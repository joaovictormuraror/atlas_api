# ATLAS API (Flask)

API em Flask para o app ATLAS — planejador de roteiros com IA.

## Instalação local
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```
A API rodará em http://127.0.0.1:8000/

## Endpoints principais
- `POST /api/register`
- `POST /api/login`
- `POST /api/upload-photo`
- `POST /api/generate-itinerary`
- `GET /api/itinerary/<id>`
- `POST /api/verify-biometric`
