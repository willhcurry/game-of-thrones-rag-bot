import os
import sys
from fastapi import FastAPI
import uvicorn

# Print environment information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"All environment variables: {dict(os.environ)}")

# Create the simplest possible FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# This needs to run whether imported or executed directly
port = int(os.environ.get("PORT", 8000))
print(f"ATTEMPTING TO BIND TO PORT {port}")

if __name__ == "__main__":
    print("Running server directly")
    uvicorn.run(app, host="0.0.0.0", port=port)
else:
    print("Imported as module")
    # This is needed for Render and other ASGI servers 