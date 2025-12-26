import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from .auth import verify_token
from .sandbox import run_in_sandbox

# Load env vars
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AutomationRequest(BaseModel):
    user_prompt: str
    
class ExecuteRequest(BaseModel):
    code: str
    env_vars: Optional[dict] = {}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/generate-script")
async def generate_script(
    request: AutomationRequest, 
    user = Depends(verify_token)
):
    try:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prompt engineering for safe code
        system_prompt = """
        You are an expert Python developer for Google Sheets automation.
        Generate a complete, runnable Python script requested by the user.
        - Do not assume local credentials. Use environment variables if needed.
        - Output python code directly.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_prompt}
            ],
            temperature=0.2
        )
        code = response.choices[0].message.content
        
         # Simple cleanup if markdown blocks are included
        if code.startswith("```python"):
            code = code.split("\n", 1)[1]
        if code.endswith("```"):
            code = code.rsplit("\n", 1)[0]

        return {"code": code, "status": "success"}
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/execute-script")
async def execute_script(
    request: ExecuteRequest, 
    user = Depends(verify_token)
):
    """
    Executes the provided script in a secure sandbox.
    User must be authenticated.
    """
    if not request.code:
        raise HTTPException(status_code=400, detail="Code is required")
        
    result = run_in_sandbox(request.code, request.env_vars)
    
    if result["status"] == "error":
        # We assume 400 for script errors, 500 for system errors, but here we just return the result
        return result
        
    return result
