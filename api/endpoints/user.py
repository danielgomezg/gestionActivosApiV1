from models import user
from models.user import Usuario
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from crud.user import create_user, get_user_all, get_user_email, authenticate_user, create_access_token
from schemas.userSchema import Response, UserSchema, UserRequest
import re

#login
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

router = APIRouter()
user.Base.metadata.create_all(bind=engine)
#print("aca: ")
#print(repr(user.Base.metadata.create_all(bind=engine)))

#def get_db():
 #   db = SessionLocal()
  #  try:
   #     yield db
    #finally:
     #   db.close()

@router.get('/users')
async def get_users(db: Session = Depends(get_db)):
    result = get_user_all(db)
    return result

@router.post('/user')
async def create(request: UserRequest, db: Session = Depends(get_db)):

    if(len(request.parameter.firstName) == 0):
        return  Response(code = "400", message = "Nombre no valido", result = [])

    if(len(request.parameter.lastName) == 0):
        return  Response(code = "400", message = "Apellido no valido", result = [])

    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    email = str(request.parameter.email)
    if(re.match(patron, email) is None):
        return Response(code = "400", message = "Email invalido", result = [])

    #valida si el mail ya esta registrado
    existeEmail = get_user_email(db, email)
    if(existeEmail):
        return Response(code="400", message="Email registrado", result=[])

    patron_rut = r'^\d{1,8}-[\dkK]$'
    rut = str(request.parameter.rut.replace(".", ""))

    if not re.match(patron_rut, rut):
        return Response(code="400", message="Rut inválido", result=[])

    _user = create_user(db, request.parameter)
    return Response(code = "201", message = "Usuario creado", result = _user).dict(exclude_none=True)

@router.post('/login')
async def login_access(request: UserRequest, db: Session = Depends(get_db)):
    _user = authenticate_user(request.parameter.email, request.parameter.password, db)
    if(_user):
        print("logged")
        access_token_expires = timedelta(minutes=60)
        print(_user.email)
        emailUser = _user.email
        access_token = create_access_token(data={"sub": emailUser}, expires_delta=access_token_expires)
        #NEW
        expire_seconds = access_token_expires.total_seconds()
        #return {"access_token": access_token, "token_type": "bearer"}
        #return Response(code="201", message="Usuario loggeado correctamente", result={"access_token": access_token, "token_type": "bearer", "expire_token":access_token_expires})
        return JSONResponse(
            content=Response(
                code="201",
                message="Usuario loggeado correctamente",
                result={"access_token": access_token, "token_type": "bearer", "expire_token": expire_seconds},
            ).dict(),
            status_code=201,
        )
    else:
        #return Response(code="401", message="Usuario incorrecto", result=[])
        raise HTTPException(status_code=401, detail="Usuario incorrecto")