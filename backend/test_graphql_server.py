"""
Minimal FastAPI app to test GraphQL endpoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import GraphQL router
from api.graphql.router import graphql_router

# Create minimal app
app = FastAPI(
    title="FinancIA GraphQL Test",
    description="Test GraphQL endpoint",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "GraphQL Test"}

# Mount GraphQL router as ASGI app
# Strawberry's GraphQLRouter is an ASGI app, not a FastAPI router
app.mount("/api/graphql", graphql_router)

if __name__ == "__main__":
    print("🚀 Starting GraphQL Test Server...")
    print("📊 GraphQL Playground: http://localhost:8000/api/graphql/")
    print("🏥 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "test_graphql_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
