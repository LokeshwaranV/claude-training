"""Main FastAPI application for Elation Health Chat Bot with Multi-Agent Orchestration."""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from routes import chat
from services.orchestrator import Orchestrator, TaskScheduler
from services.rag_engine import ClinicalRAG

# Initialize observability (optional)
try:
    from observability.telemetry import TelemetrySetup, MetricsCollector
    telemetry = TelemetrySetup(
        service_name="elation-chatbot",
        enabled=os.getenv("OTEL_ENABLED", "false").lower() == "true"
    )
    telemetry.setup()
    metrics_collector = MetricsCollector(telemetry)
except ImportError:
    telemetry = None
    metrics_collector = None
    print("⚠️  OpenTelemetry not available (optional feature)")

# Initialize orchestration
orchestrator = Orchestrator()
scheduler = TaskScheduler(orchestrator)

# Initialize RAG
rag_engine = ClinicalRAG()

# Create FastAPI app
app = FastAPI(
    title="Elation Health Chat Bot",
    description="AI-powered clinical documentation assistant with multi-agent orchestration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React frontend static files
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    print("🚀 Starting Elation Health Chat Bot v2.0...")
    print("⚡ Running with Groq + Open-Source LLMs (Llama 3.1/Mixtral)")

    # Verify API keys
    if os.getenv("GROQ_API_KEY"):
        print("✅ GROQ_API_KEY configured - using Groq for fast inference")
    else:
        print("⚠️  WARNING: GROQ_API_KEY not set. Using Groq demo key.")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ℹ️  ANTHROPIC_API_KEY not set. Secondary AI features will be limited.")

    # Initialize observability
    if telemetry and hasattr(telemetry, 'enabled') and telemetry.enabled:
        print("✅ OpenTelemetry initialized")
    else:
        print("ℹ️  OpenTelemetry disabled (optional)")

    # Initialize orchestration
    print(f"✅ Multi-agent orchestrator initialized")

    # Initialize RAG
    print(f"✅ Clinical RAG engine initialized")
    print(f"   - Topics in knowledge base: {len(rag_engine.knowledge_base)}")

    print("🏥 Elation Health Chat Bot ready!")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    print("Shutting down Elation Health Chat Bot...")
    if metrics_collector:
        stats = metrics_collector.get_statistics()
        print(f"Session statistics: {stats}")


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Elation Health Chat Bot v2.1.0",
        "version": "2.1.0",
        "status": "running",
        "features": {
            "groq_integration": bool(os.getenv("GROQ_API_KEY")),
            "modern_ui": True,
            "dark_mode": True,
            "rag_engine": True,
            "observability": (telemetry and hasattr(telemetry, 'enabled') and telemetry.enabled) if telemetry else False
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/api/chat",
            "orchestration": "/api/orchestration",
            "rag": "/api/rag"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "elation-health-chatbot",
        "version": "2.1.0",
        "features": {
            "groq_integration": True,
            "modern_ui": True,
            "dark_mode": True
        },
        "components": {
            "api": "operational",
            "orchestrator": "operational",
            "rag_engine": "operational",
            "observability": "operational" if (telemetry and hasattr(telemetry, 'enabled') and telemetry.enabled) else "disabled",
            "frontend": "operational"
        }
    }


@app.get("/api/orchestration/status")
async def orchestration_status():
    """Get orchestration status."""
    return {
        "agent_status": orchestrator.get_agent_status(),
        "statistics": orchestrator.get_statistics()
    }


@app.get("/api/rag/knowledge")
async def rag_knowledge():
    """Get RAG engine knowledge base info."""
    return {
        "topics": list(rag_engine.knowledge_base.keys()),
        "total_documents": len(rag_engine.documents),
        "statistics": rag_engine.get_retrieval_stats()
    }


@app.get("/api/rag/retrieve")
async def rag_retrieve(query: str, top_k: int = 3):
    """Retrieve relevant clinical documents."""
    docs = rag_engine.retrieve_relevant_documents(query, top_k)
    return {
        "query": query,
        "results": [
            {
                "id": doc.id,
                "content": doc.content[:200] + "...",
                "source": doc.source
            }
            for doc in docs
        ]
    }


@app.post("/api/rag/guidelines")
async def rag_guidelines(condition: str):
    """Get clinical guidelines for a condition."""
    guidelines = rag_engine.retrieve_by_condition(condition)
    return guidelines


@app.get("/api/metrics")
async def metrics():
    """Get collected metrics."""
    return metrics_collector.get_statistics()


# Include routers
app.include_router(chat.router)


# Serve React frontend for all non-API routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve React frontend for all non-API routes."""
    # Skip API routes and static files
    if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("docs") or full_path.startswith("openapi"):
        return JSONResponse({"error": "Not found"}, status_code=404)

    # Serve React index.html for all other routes
    frontend_build_path = Path(__file__).parent.parent / "frontend" / "build" / "index.html"
    if frontend_build_path.exists():
        return FileResponse(frontend_build_path)
    return JSONResponse({"error": "Frontend not built"}, status_code=404)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle global exceptions."""
    if telemetry and hasattr(telemetry, 'tracer') and telemetry.tracer:
        telemetry.tracer.set_attribute("error", str(exc))
    if metrics_collector:
        metrics_collector.telemetry.record_metric("api.errors.total", 1)

    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "service": "elation-chatbot"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
