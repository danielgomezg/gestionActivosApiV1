from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
import json
#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
from fastapi.responses import JSONResponse

from api.endpoints import user
from api.endpoints import company
from api.endpoints import profile
from api.endpoints import office
from api.endpoints import sucursal
from api.endpoints import action
from api.endpoints import profileAction
from api.endpoints import article
from api.endpoints import active
from api.endpoints import history
from api.endpoints import generation_catalogo
from api.endpoints import category

#cors
from fastapi.middleware.cors import CORSMiddleware
from decouple import config

#DB
from sqlalchemy.orm import Session
from database import get_db, engine, SessionLocal

#middleware
from crud.profileAction import get_profile_action_by_id_profile_action
from crud.action import get_action_by_name

# models
import re

from models import user as user_model
from models import company as company_model
from models import profile as profile_model
from models import office as office_model
from models import sucursal as sucursal_model
from models import action as action_model
from models import profile_action as profile_action_model
from models import article as article_model
from models import active as active_model
from models import history as history_model
from models import category as category_model



user_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:5173",
    "http://45.33.99.148"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Variables
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

# Middleware para las rutas
@app.middleware("http")
def middleware_validacion_permisos( request: Request, call_next):

    # Verifica si es una solicitud OPTIONS y omitir la lógica de validación
    if request.method == "OPTIONS":
        return call_next(request)

    # Path
    path_peticion = request.url.path.split("/")[1]

    if (path_peticion == "login" or path_peticion == "token" or path_peticion == "docs" or path_peticion == "openapi.json"):
        return call_next(request)

    #token
    authorization_header = request.headers.get("Authorization")

    # Base de datos
    db = SessionLocal()

    if authorization_header and authorization_header.startswith("Bearer "):
        token_value = authorization_header.split(" ")[1]
        #print(f"Valor del token: {token_value}")

        try:
            credentials = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = credentials.get("sub")
            profile_id = credentials.get("profile")
            #print(f"ID del usuario: {user_id}")

            diccionario = {
                "GET": "get",
                "POST": "create",
                "PUT": "update",
                "DELETE": "delete"
            }

            # Se contruye el nombre de la accion
            if (re.search(r'user', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "usuario"
            elif (re.search(r'compan', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "empresa"

            elif (re.search(r'sucursal', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "sucursal"

            elif (re.search(r'office', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "oficina"

            elif (re.search(r'action', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "accion"

            elif (re.search(r'profile', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "perfil"

            elif (re.search(r'active', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "activo"

            elif (re.search(r'article', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "articulo"

            elif (re.search(r'histor', path_peticion, flags=re.IGNORECASE)):
                nombre_accion = diccionario.get(request.method) + "-" + "historial"

            elif (re.search(r'report', path_peticion, flags=re.IGNORECASE)):
                #nombre_accion = diccionario.get(request.method) + "-" + "historial"
                return call_next(request)

            elif (re.search(r'categor', path_peticion, flags=re.IGNORECASE)):
                #nombre_accion = diccionario.get(request.method) + "-" + "historial"
                return call_next(request)

            else:
                return JSONResponse(content={"detail": "La accion a realizar no existe"}, status_code=401)

            print(nombre_accion)
            accion = get_action_by_name(db, nombre_accion)
            action_id = accion.id
            profile_action = get_profile_action_by_id_profile_action(db, profile_id, action_id)
            # print(profile_action)

            if (profile_action is None):
                print("No tienes permisos para realizar esta acción 1")
                return JSONResponse(content={"detail": "No tienes permisos para realizar esta acción"}, status_code=401)

        except JWTError:
            print ("Error al decodificar el token 2")
            raise HTTPException(status_code=401, detail="Error al decodificar el token")





    # Llama a la siguiente función en la cadena de middlewares y rutas
    response = call_next(request)

    # Lógica después de la ruta
    print("Peticion realizada con exito")

    return response

#print("main")  # Añade esta línea
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(company.router)
app.include_router(sucursal.router)
app.include_router(office.router)
app.include_router(action.router)
app.include_router(profileAction.router)
app.include_router(category.router)
app.include_router(article.router)
app.include_router(active.router)
app.include_router(history.router)
app.include_router(generation_catalogo.router)

