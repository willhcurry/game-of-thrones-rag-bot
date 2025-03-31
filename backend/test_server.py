from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Print debugging information
port = int(os.environ.get("PORT", "8000"))
print(f"Starting server on port {port}")
print(f"Environment variables:")
print(f"PORT={os.environ.get('PORT')}")
print(f"GUNICORN_CMD_ARGS={os.environ.get('GUNICORN_CMD_ARGS')}")
print(f"Current working directory: {os.getcwd()}")

# This needs to run whether the file is imported or run directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 