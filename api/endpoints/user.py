from models import user
from models.user import Usuario
# from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from crud.user import create_user, get_user_all, get_user_email, authenticate_user, create_access_token, get_user_disable_current, get_user_by_id, update_user, delete_user, search_users_by_mail_rut
from schemas.userSchema import UserSchema, UserEditSchema, UserSchemaLogin
from schemas.schemaGenerico import Response, ResponseGet
import re
from typing import Tuple
from crud.profile import get_profile_by_id
from crud.company import get_company_by_id

import json
#login
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from decouple import config


router = APIRouter()
# user.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer("/token")

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

@router.get("/user/{id}")
def get_user(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result = get_user_by_id(db, id)
    if result is None:
        return Response(code="404", result=[], message="Usuario no encontrado").model_dump()
    return Response(code= "200", message="Usuario encontrado", result = result).model_dump()

@router.get('/users')
def get_users(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = get_user_all(db, limit, offset)
    if not result:
        return ResponseGet(code= "404", result = [], limit= limit, offset = offset, count = 0).model_dump()
    return ResponseGet(code= "200", result = result, limit= limit, offset = offset, count = count).model_dump()

@router.get('/users/search')
def search_users(search: str, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    name_user, expiration_time = current_user_info
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    result, count = search_users_by_mail_rut(db, search, limit, offset)
    if not result:
        return ResponseGet(code="200", result=[], limit=limit, offset=offset, count=0).model_dump()
    return ResponseGet(code="200", result=result, limit=limit, offset=offset, count=count).model_dump()

@router.post('/user')
def create(request: UserSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if(len(request.firstName) == 0):
        return  Response(code = "400", message = "Nombre no valido", result = [])

    if(len(request.lastName) == 0):
        return  Response(code = "400", message = "Apellido no valido", result = [])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    email = str(request.email)
    if(re.match(patron, email) is None):
        return Response(code = "400", message = "Email invalido", result = [])

    #valida si el mail ya esta registrado
    existeEmail = get_user_email(db, email)
    if(existeEmail):
        return Response(code="400", message="Email registrado", result=[])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.rut.replace(".", ""))

    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut inválido", result=[])

    if (request.company_id is not None):
        id_compania = get_company_by_id(db, request.company_id)
        if (not id_compania):
            return Response(code="400", message="id compania no valido", result=[])

    id_perfil = get_profile_by_id(db, request.profile_id)
    if (not id_perfil):
        return Response(code="400", message="id perfil no valido", result=[])

    _user = create_user(db, request)
    return Response(code = "201", message = f"Usuario {_user.firstName} creado", result = _user).model_dump()

@router.put('/user/{id}')
def update(request: UserEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    if (len(request.firstName) == 0):
        return Response(code="400", message="Nombre no valido", result=[])

    if (len(request.lastName) == 0):
        return Response(code="400", message="Apellido no valido", result=[])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    email = str(request.email)
    if (re.match(patron, email) is None):
        return Response(code="400", message="Email invalido", result=[])

    # valida si el mail ya esta registrado
    existeEmail = get_user_email(db, email)
    if (existeEmail and id != existeEmail.id):
        return Response(code="400", message="Email registrado", result=[])

    if (request.company_id is not None):
        id_compania = get_company_by_id(db, request.company_id)
        if (not id_compania):
            return Response(code="400", message="id compania no valido", result=[])

    id_perfil = get_profile_by_id(db, request.profile_id)
    if (not id_perfil):
        return Response(code="400", message="id perfil no valido", result=[])

    _user = update_user(db, id, request)
    return Response(code = "201", message = f"Usuario {_user.firstName} editado", result = _user).model_dump()

@router.delete('/user/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    name_user, expiration_time = current_user_info
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    _user = delete_user(db, id)
    return Response(code = "201", message = f"Usuario con id {id} eliminado", result = _user).model_dump()

@router.post('/login')
def login_access(request: UserSchemaLogin, db: Session = Depends(get_db)):
    _user = authenticate_user(request.email, request.password, db)
    if(_user):
        access_token_expires = timedelta(minutes=300)
        user_id = str(_user.id)

        additional_info = {
            "email": _user.email,
            "firstName": _user.firstName,
            "lastName": _user.lastName,
            "secondName": _user.secondName,
            "secondLastName": _user.secondLastName,
            "rut": _user.rut,
            "profile_id": _user.profile_id,
            "company_id": _user.company_id,
            "id": _user.id
        }

        access_token = create_access_token(data={"sub": user_id, "profile": _user.profile_id, "user": additional_info},expires_delta=access_token_expires)

        expire_seconds = access_token_expires.total_seconds()
        
        return JSONResponse(
            content=Response(
                code="201",
                message="Usuario loggeado correctamente",
                result = {
                    "access_token": access_token, 
                    "token_type": "bearer", 
                    "expire_token": expire_seconds,
                    "user": additional_info
                },
            ).model_dump(),
            status_code=201,
        )
    else:
        return Response(code="401", message="Usuario incorrecto", result=[])

@router.post('/token')
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    _user = authenticate_user(form_data.username, form_data.password, db)
    if(_user):
        access_token_expires = timedelta(minutes=180)
        user_id = str(_user.id)

        additional_info = {
            "email": _user.email,
            "firstName": _user.firstName,
            "lastName": _user.lastName,
            "secondName": _user.secondName,
            "secondLastName": _user.secondLastName,
            "rut": _user.rut,
            "profile_id": _user.profile_id,
            "company_id": _user.company_id,
            "id": _user.id
        }

        access_token = create_access_token(data={"sub": user_id, "profile": _user.profile_id, "user": additional_info},expires_delta=access_token_expires)

        #NEW
        expire_seconds = access_token_expires.total_seconds()

        return {"access_token": access_token, "token_type": "bearer", "expire_token": expire_seconds}
    else:
        raise HTTPException(status_code=401, detail="Usuario incorrecto")