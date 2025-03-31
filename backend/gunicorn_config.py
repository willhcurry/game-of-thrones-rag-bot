import os

# Get the port from environment variable
port = os.environ.get("PORT", 8000)

# Gunicorn config
bind = f"0.0.0.0:{port}"
workers = 1  # Start with 1 worker for the free tier
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5 