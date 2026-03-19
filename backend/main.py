from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import engine, Base
from backend.api.v1 import clients

# Crear de forma automática las tablas en la base de datos (para desarrollo / MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS Agency Backend",
    description="Fase 1 de la plataforma SaaS multi-tenant para gestiones de marketing",
    version="0.1.0"
)

# Habilitar CORS para permitir peticiones del Frontend en la nube
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los endpoints de nuestra API
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])

from fastapi.staticfiles import StaticFiles
import os

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {
        "message": "Bienvenido al Backend de la Plataforma SaaS", 
        "docs": "/docs"
    }
