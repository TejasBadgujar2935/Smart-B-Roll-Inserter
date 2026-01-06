"""
Simple script to run the FastAPI server locally.
"""

import os
import uvicorn

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='sk-your-key'")
        print()
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Smart B-Roll Inserter API server...")
    print(f"   Server: http://localhost:{port}")
    print(f"   Docs: http://localhost:{port}/docs")
    print(f"   Health: http://localhost:{port}/health")
    print()
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

