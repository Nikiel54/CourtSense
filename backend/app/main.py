#### MAIN ENTRY POINT OF THE APP ####

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from app.apis import predictions


app = FastAPI(
    title="NBA Prediction API",
    description="ELO-based NBA game predictions with real-time ratings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

load_dotenv()

## Connection to front end
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv('CORS_ORIGINS'),  # React dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "Worlds"}



## Handle api endpoints ftom other files
app.include_router(predictions.router, prefix="/apis", tags=["predictions"])