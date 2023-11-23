from fastapi import FastAPI
#from api.endpoints import company
from api.endpoints import user
from api.endpoints import company
from api.endpoints import office
from api.endpoints import sucursal
#cors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
origins = [
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user.router)
app.include_router(company.router)
app.include_router(office.router)
app.include_router(sucursal.router)