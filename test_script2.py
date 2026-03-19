import subprocess
import time
import httpx
from app.db.database import engine, Base
import json

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Arrancando uvicorn en puerto 8001...")
p = subprocess.Popen(['uvicorn', 'app.main:app', '--port', '8001'])
time.sleep(3)

try:
    # 1. Onboarding
    resp = httpx.post("http://127.0.0.1:8001/api/v1/clients/onboarding", json={
        "company_name": "Hormiglass",
        "website_url": "https://www.hormiglass.cl/"
    }, timeout=30.0)
    client_id = resp.json()["id"]
    print(f"Onboarding finalizado. ID: {client_id}")

    # 2. Guion
    resp2 = httpx.post(f"http://127.0.0.1:8001/api/v1/clients/{client_id}/generate-script", json={
        "product_name": "Pastelones antideslizantes",
        "product_description": "Nuevos pastelones de hormigón antideslizantes para piscinas"
    }, timeout=60.0)
    if resp2.status_code == 200:
        print("--- RESULTADO DEL SCRIPT ---")
        print(json.dumps(resp2.json(), indent=2, ensure_ascii=False))
    else:
        print("Error:", resp2.text)
finally:
    p.terminate()
