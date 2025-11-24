#!/bin/bash
# Start Flask API server

cd "$(dirname "$0")"
source venv/bin/activate
python src/api/app.py

