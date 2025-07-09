from fastapi import FastAPI
from .api.api import router as api_router

# construct the app and add the routes of api
app = FastAPI()
app.include_router(api_router)