from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.app.routers import calculator_router, pvgis_router, pvgis_plus_router, utils_router

app = FastAPI(title="Solar Project", version="0.1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calculator_router.router)
app.include_router(pvgis_router.router)
app.include_router(pvgis_plus_router.router)
app.include_router(utils_router.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Solar Project API"}
