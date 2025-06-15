#/bin/bash

# /usr/sbin/tailscaled & 
# tailscale up

# echo "Sleeping for 5s"
# sleep 5

cd /app
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
