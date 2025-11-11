from fastapi import FastAPI
from api.app.routers import test_router, calculator_router

app = FastAPI(title="Solar Project", version="0.1")

# Include routers
app.include_router(test_router.router)
app.include_router(calculator_router.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Solar Project API"}
