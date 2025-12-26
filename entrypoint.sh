#!/bin/bash
WEBHOOK_URL="https://discord.com/api/webhooks/1454237330595516486/qRNCSey4p-dCgPpOQStZZxnnigp_cDdxJI9I5UKZ9LGR4opaUfv8s-8FPIzgHp1kiOWK"

# Send start message
curl -H "Content-Type: application/json" -d '{"content": "🚀 Deployment started! Compiling report..."}' "$WEBHOOK_URL"

# Compile report
if [ -d "rapport" ] && [ -f "rapport/rapport.tex" ]; then
    echo "Compiling rapport.tex..."
    cd rapport
    # Run twice for references if needed, but once is usually enough for a simple check
    pdflatex -interaction=nonstopmode rapport.tex
    cd ..
else
    echo "Rapport directory or file not found."
fi

# Send end message
curl -H "Content-Type: application/json" -d '{"content": "✅ Report compiled. Starting Flask server..."}' "$WEBHOOK_URL"

# Start Flask
export FLASK_APP=app.py
# Use python -m flask to ensure we use the installed module

curl -H "Content-Type: application/json" -d '{"content": "✅ Server is started !"}' "$WEBHOOK_URL"
curl -H "Content-Type: application/json" -d '{"content": "--------------------------------------"}' "$WEBHOOK_URL"


python3 -m flask run --host=0.0.0.0

