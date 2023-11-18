from models import user
from models.user import Usuario
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.user import create_user
from schemas.userSchema import Response, UserSchema, UserRequest
import re

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
async def get_users():
    return "get users..."

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

    _user = create_user(db, request.parameter)
    return Response(code = "201", message = "Usuario creado", result = _user).dict(exclude_none=True)