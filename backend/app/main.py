import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI
import logging
from pydantic import BaseModel
from typing import Optional
import subprocess
import docker  # For sandboxed execution

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load env vars
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Initialize Docker client (for sandbox)
docker_client = docker.from_env()


class AutomationRequest(BaseModel):
    user_prompt: str
    google_token: Optional[str] = None


@app.post("/generate-script")
async def generate_script(request: AutomationRequest):
    try:
        # Verify user token with Firebase (pseudo-code)
        # user = verify_firebase_token(request.google_token)

        # Generate code with GPT-4
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate secure Python code for Google Sheets automation."},
                {"role": "user", "content": request.user_prompt}
            ],
            temperature=0.3
        )
        code = response.choices[0].message.content

        return {"code": code, "status": "success"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/execute-script")
async def execute_script(code: str, token: str = Depends(oauth2_scheme)):
    try:
        # Sandbox execution in Docker
        container = docker_client.containers.run(
            "python:3.9-slim",
            command=f"python -c '{code}'",
            volumes={'google-creds.json': {'bind': '/creds.json', 'mode': 'ro'}},
            environment={"GOOGLE_APPLICATION_CREDENTIALS": "/creds.json"},
            remove=True
        )
        return {"status": "success", "logs": container.decode()}
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Automation failed")

# Health check


@app.get("/health")
async def health():
    return {"status": "healthy"}
