#!/bin/bash

echo "=============================="
echo " Iniciando Garcold POS Backend"
echo "=============================="

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000