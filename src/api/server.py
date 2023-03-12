from fastapi import FastAPI
from uvicorn import run

from src.api.routes import predictions_router, root_router

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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
    )
