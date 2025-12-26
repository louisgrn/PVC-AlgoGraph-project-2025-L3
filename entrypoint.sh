#!/bin/bash
WEBHOOK_URL="https://discord.com/api/webhooks/1454237330595516486/qRNCSey4p-dCgPpOQStZZxnnigp_cDdxJI9I5UKZ9LGR4opaUfv8s-8FPIzgHp1kiOWK"

# Send start message
curl -H "Content-Type: application/json" -d '{"content": "🚀 Deployment started! Starting Flask server..."}' "$WEBHOOK_URL"

# Start Flask
export FLASK_APP=app.py
# Use python -m flask to ensure we use the installed module

python3 -m flask run --host=0.0.0.0

curl -H "Content-Type: application/json" -d '{"content": "✅ Server is started !"}' "$WEBHOOK_URL"
curl -H "Content-Type: application/json" -d '{"content": "--------------------------------------"}' "$WEBHOOK_URL"



