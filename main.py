from fastapi import FastAPI
from api.endpoints import company

app = FastAPI()

app.include_router(company.router)