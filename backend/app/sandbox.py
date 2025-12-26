import docker
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

def run_in_sandbox(code: str, env_vars: dict = None) -> dict:
    """
    Executes Python code in a secure Docker sandbox.
    
    Security measures:
    1. Code is written to a temp file and mounted (prevents shell injection).
    2. No host credentials are mounted.
    3. Resource limits applied (memory, cpu).
    4. Auto-removal of container.
    """
    client = docker.from_env()
    
    # Create a temp file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(code)
        temp_script_path = temp_script.name

    container = None
    try:
        # Prepare environment variables
        environment = env_vars or {}
        
        # Run container
        # We mount the temp script to /app/script.py and run it.
        container = client.containers.run(
            "python:3.9-slim",
            command=["python", "/app/script.py"],  # List form avoids shell execution
            volumes={
                temp_script_path: {'bind': '/app/script.py', 'mode': 'ro'}
            },
            environment=environment,
            # Security limits
            mem_limit="128m",
            cpu_quota=50000, # 50% of 1 CPU
            network_mode="bridge", # Allow fetching packages/api calls if needed, consider "none" for stricter security
            detach=True,
            stdout=True,
            stderr=True
        )
        
        # Wait for result with timeout
        exit_code = container.wait(timeout=30)
        logs = container.logs().decode('utf-8')
        
        return {
            "status": "success" if exit_code['StatusCode'] == 0 else "error",
            "output": logs,
            "exit_code": exit_code['StatusCode']
        }

    except Exception as e:
        logger.error(f"Sandbox execution failed: {str(e)}")
        # Try to get logs if container started
        logs = ""
        if container:
            try:
                logs = container.logs().decode('utf-8') 
            except: 
                pass
        return {"status": "error", "output": str(e) + "\n" + logs}
        
    finally:
        # Cleanup
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)
