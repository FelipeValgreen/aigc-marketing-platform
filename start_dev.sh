#!/bin/bash
echo "🚀 Iniciando AIGC Platform (Localhost)..."

# Matar procesos colgados
echo "🧹 Asegurando que nada bloquee los puertos..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "🧠 Levantando Backend (FastAPI)..."
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000 &

echo "💻 Compilando y Levantando UI (Next.js)..."
npm run dev
