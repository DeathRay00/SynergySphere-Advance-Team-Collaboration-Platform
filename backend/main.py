#!/usr/bin/env python3
"""
Main entry point for the SynergySphere backend API
"""

import uvicorn
from server import app

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
