#!/bin/bash
cd /content
rm -rf MotorTriage_app
git clone -q https://github.com/alexsouye09-lds/Motortriage.git MotorTriage_app
cd MotorTriage_app
ls app.py m_*.pkl requirements.txt || { echo "Fichiers manquants dans le dépôt GitHub"; exit 1; }

pip install -q -r requirements.txt

pkill -f "streamlit run" ; pkill -f cloudflared ; sleep 1
[ -x /content/cloudflared ] || { wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared && chmod +x /content/cloudflared; }

nohup streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false > /content/logs.txt 2>&1 &
sleep 8
nohup /content/cloudflared tunnel --url http://localhost:8501 > /content/tunnel.txt 2>&1 &

url=""
for i in $(seq 1 30); do
  url=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /content/tunnel.txt | head -1)
  [ -n "$url" ] && break
  sleep 2
done
echo "=============================="
echo "LIEN : ${url:-pas prêt, relance (voir /content/tunnel.txt)}"
echo "=============================="
