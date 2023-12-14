from models import user
from models.user import Usuario
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from crud.user import create_user, get_user_all, get_user_email, authenticate_user, create_access_token, get_user_disable_current, get_user_by_id, update_user, delete_user
from schemas.userSchema import Response, UserSchema, UserEditSchema, UserSchemaLogin
import re
from typing import Tuple
#importaciones para obtener ids
#from api.endpoints.profile import get_profile_by_id
#from api.endpoints.company import get_company_by_id
from crud.profile import get_profile_by_id
from crud.company import get_company_by_id

#login
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from decouple import config


router = APIRouter()
user.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer("/token")

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

@router.get("/user/{id}", response_model=UserSchema)
async def get_user(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    result = get_user_by_id(db, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return result

@router.get('/users')
async def get_users(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), limit: int = 25, offset: int = 0):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    result = get_user_all(db, limit, offset)
    return result

@router.post('/user')
async def create(request: UserSchema, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

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
    return Response(code = "201", message = "Usuario creado", result = _user).dict(exclude_none=True)

@router.put('/user/{id}')
async def update(request: UserEditSchema, id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

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
    print(_user)
    return Response(code = "201", message = "Usuario editado", result = _user).dict(exclude_none=True)

@router.delete('/user/{id}')
async def delete(id: int, db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current)):
    id_user, expiration_time = current_user_info
    print("Tiempo de expiración: ", expiration_time)
    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="Su sesión ha expirado", result=[])

    _user = delete_user(db, id)
    return Response(code = "201", message = f"Usuario con id {id} eliminado", result = _user).dict(exclude_none=True)

@router.post('/login')
async def login_access(request: UserSchemaLogin, db: Session = Depends(get_db)):
    _user = authenticate_user(request.email, request.password, db)
    if(_user):
        access_token_expires = timedelta(minutes=60)
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
        access_token = create_access_token(data = {"sub": user_id, "profile": _user.profile_id }, expires_delta=access_token_expires)

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
            ).dict(),
            status_code=201,
        )
    else:
        #return Response(code="401", message="Usuario incorrecto", result=[])
        raise HTTPException(status_code=401, detail="Usuario incorrecto")

@router.post('/token')
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    _user = authenticate_user(form_data.username, form_data.password, db)
    if(_user):
        access_token_expires = timedelta(minutes=60)
        user_id = str(_user.id)
        access_token = create_access_token(data={"sub": user_id}, expires_delta=access_token_expires)

        #NEW
        expire_seconds = access_token_expires.total_seconds()

        return {"access_token": access_token, "token_type": "bearer", "expire_token": expire_seconds}
        #return Response(code="201", message="Usuario loggeado correctamente", result={"access_token": access_token, "token_type": "bearer", "expire_token":access_token_expires})
       # return JSONResponse(
        #    content=Response(
         #       code="201",
          #      message="Usuario loggeado correctamente",
           #     result={"access_token": access_token, "token_type": "bearer", "expire_token": expire_seconds},
            #).dict(),
            #status_code=201,
        #)
    else:
        #return Response(code="401", message="Usuario incorrecto", result=[])
        raise HTTPException(status_code=401, detail="Usuario incorrecto")