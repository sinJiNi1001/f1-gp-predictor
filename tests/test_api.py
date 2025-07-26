import pytest
import requests
import time
import subprocess
import os
import logging
import sys
from pathlib import Path
from typing import Generator, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be available"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

@pytest.fixture(scope="session")
def api_server() -> Generator[subprocess.Popen, None, None]:
    """Start and manage FastAPI server"""
    logger.info("Starting FastAPI server...")
    
    # Get project root
    root_dir = Path(__file__).parent.parent
    
    # Start server process
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(root_dir),
        env={**os.environ, "PYTHONPATH": str(root_dir)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server
    if not wait_for_server("http://localhost:8000/health"):
        out, err = server.communicate()
        logger.error(f"Server failed to start:\nOutput: {out}\nError: {err}")
        pytest.skip("Server failed to start")
        
    yield server
    
    # Cleanup
    logger.info("Shutting down server...")
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()

@pytest.mark.asyncio
async def test_prediction(api_server: subprocess.Popen) -> None:
    """Test race prediction endpoint"""
    data = {
        "year": 2023,
        "grand_prix": "British Grand Prix"
    }
    
    response = requests.post(
        "http://localhost:8000/predict",
        json=data,
        timeout=5
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "predicted_winner" in result