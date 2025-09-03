import subprocess
import sys
import time
import socket
import os
import pytest

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8000))


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
            return True
        except Exception:
            return False


def test_server():
    """Test that the FastAPI dev server starts and listens on the expected port."""
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "truledgr_api.main:app", "--host", HOST, "--port", str(PORT)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        # Wait up to 10 seconds for the server to start
        for _ in range(20):
            if is_port_open(HOST, PORT):
                break
            time.sleep(0.5)
        else:
            pytest.fail(f"Server did not start on {HOST}:{PORT} within timeout.")
        # Optionally, check the server's /health endpoint here
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
