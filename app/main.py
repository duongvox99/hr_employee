from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.employee_router import router as employee_router

app = FastAPI(
    title="HR Employee API",
    description="HR Employee management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employee_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
