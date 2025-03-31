from fastapi import FastAPI
import uvicorn
import os
from api import app  # Import your existing FastAPI app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
