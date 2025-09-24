#!/bin/bash

echo "Starting Internal API..."
python3 /app/internal_api.py &

echo "Starting Stock API..."
python3 /app/stock_api.py &

echo "Starting Main Backend API..."
python3 /app/backend.py