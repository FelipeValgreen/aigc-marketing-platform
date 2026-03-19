from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

# Esquemas para Cliente
class ClientBase(BaseModel):
    company_name: str
    website_url: HttpUrl

class ClientCreate(ClientBase):
    pass

class ScriptRequest(BaseModel):
    product_name: str
    product_description: str

class GenerateAudioRequest(BaseModel):
    script_text: str
    product_name: str = "Producto"

class ProjectCreate(BaseModel):
    client_id: int
    product_name: str
    product_desc: str
    video_angle: str

class ProjectOut(ProjectCreate):
    id: int
    status: str
    script_json: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ClientOut(ClientBase):
    id: int
    agency_id: Optional[int] = None
    created_at: datetime
    # Convertimos la URL a string en la respuesta si lo preferimos, 
    # aunque Pydantic V2 serializa HttpUrl como string a JSON por defecto.

    class Config:
        from_attributes = True
