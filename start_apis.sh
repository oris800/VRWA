#!/bin/sh
set -e

echo "Starting public stock_api on port 8200..."
python3 stock_api.py &

echo "Starting hidden internal_api on a secret random port..."
python3 internal_api.py &

# המתן לסיום של התהליך האחרון שהורץ ברקע
wait $!