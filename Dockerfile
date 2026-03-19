FROM python:3.11-slim

# Evitar que python escriba *.pyc
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar FFmpeg en el SO base
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Crear infraestructura base y dar permisos totales para el usuario no-root de Hugging Face
RUN mkdir -p static/video static/audio static/vtt static/uploads static/music
RUN chmod -R 777 /app

# Exponer puerto 7860 (REQUERIDO POR HUGGING FACE SPACES)
EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
