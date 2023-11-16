from fastapi import FastAPI
#from api.endpoints import company
from api.endpoints import user

app = FastAPI()

#app.include_router(company.router)
app.include_router(user.router)