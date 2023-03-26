from os import getenv

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from uvicorn import run

from src.api.routes import predictions_router, root_router

load_dotenv(find_dotenv())
API_HOST: str = getenv("API_HOST")
API_PORT: int = int(getenv("API_PORT"))

API_V1_STR: str = "/api/v1"
app = FastAPI(
    title="NYC taxis total tip amount prediction",
    description="RESTful API to predict how much a taxi ride will cost.",
    version="0.1.0",
    license_info={"name": "MIT"},
)
app.include_router(root_router, prefix=API_V1_STR, tags=["root"])
app.include_router(predictions_router, prefix=API_V1_STR, tags=["predictions"])

if __name__ == "__main__":
    run(
        app="src.api.server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="debug",
    )
