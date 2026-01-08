"""Main FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="Portfolio Tracker",
    description="Crypto portfolio tracking service",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Portfolio Tracker API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
