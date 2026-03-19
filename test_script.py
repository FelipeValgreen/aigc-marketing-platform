from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine, Base
import os
import json

# Recrear la DB para tener las nuevas columnas de la orden 04
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def run_test():
    print("▶️ Enviando petición de onboarding...")
    resp = client.post("/api/v1/clients/onboarding", json={
        "company_name": "Hormiglass",
        "website_url": "https://www.hormiglass.cl/"
    })
    
    if resp.status_code != 201:
        print("Error en onboarding:", resp.text)
        return
        
    client_id = resp.json()["id"]
    print(f"✅ Onboarding finalizado. Cliente ID: {client_id}")
    
    print("▶️ Pidiendo generación de guion...")
    resp2 = client.post(f"/api/v1/clients/{client_id}/generate-script", json={
        "product_name": "Pastelones antideslizantes",
        "product_description": "Nuevos pastelones de hormigón antideslizantes para piscinas"
    })
    
    if resp2.status_code == 200:
        print("--- RESULTADO DEL SCRIPT ---")
        print(json.dumps(resp2.json(), indent=2, ensure_ascii=False))
    else:
        print("Error generando el guion:", resp2.text)

if __name__ == "__main__":
    run_test()
