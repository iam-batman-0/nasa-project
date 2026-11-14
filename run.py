"""
BioSentinel Launcher Script.
Starts the FastAPI application on http://localhost:8000.
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("  NASA BioSentinel - Autonomous Spaceflight Health System")
    print("  Running on: http://localhost:8000")
    print("  Offline Edge System • Zero Ground Support Dependency")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

