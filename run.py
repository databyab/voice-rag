import sys
import os
import subprocess

# Auto-switch to .venv python if running from global system python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
if os.name != "nt":
    venv_python = os.path.join(BASE_DIR, ".venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable.lower() != os.path.abspath(venv_python).lower():
    print(f"--> Virtualenv detected. Switching Python interpreter to: {venv_python}")
    subprocess.run([venv_python, __file__] + sys.argv[1:])
    sys.exit(0)

import uvicorn
from app.config import settings
from app.utils.logging import logger

def main():
    print("=" * 60)
    print("      Pipecat + RAG Conversational AI Assistant")
    print("=" * 60)
    
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        print("\n[WARNING] GROQ_API_KEY is missing or set to placeholder in .env!")
        print("Please edit .env and set your valid Groq API key from https://console.groq.com/\n")
    else:
        print(f"[OK] Groq API Key detected. Model: {settings.GROQ_MODEL}")

    print(f"[OK] Vector Storage Path: {settings.CHROMA_PATH}")
    print(f"[OK] Local Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"[OK] Launching Server on http://{settings.HOST}:{settings.PORT}")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
