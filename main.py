from fastapi import FastAPI

#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from api.endpoints import user
from api.endpoints import company
from api.endpoints import profile
from api.endpoints import office
from api.endpoints import sucursal
from api.endpoints import action
from api.endpoints import profileAction



#cors
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#print("main")  # Añade esta línea
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(company.router)
app.include_router(sucursal.router)
app.include_router(office.router)
app.include_router(action.router)
app.include_router(profileAction.router)

