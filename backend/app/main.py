#### MAIN ENTRY POINT OF THE APP ####

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from apis import predictions


app = FastAPI(
    title="NBA Prediction API",
    description="ELO-based NBA game predictions with real-time ratings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

## Connection to front end
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
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