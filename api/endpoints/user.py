from models import user
from models.user import Usuario
from database import engine
from fastapi import APIRouter, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.user import create_user
from helpers.schema import Response, UserSchema, UserRequest

router = APIRouter()
#user.Base.metadata.create_all(bind=engine)

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
    _user = create_user(db, request.parameter)
    return Response(code = "201", status = "OK", message = "Usuario creado", result = _user).dict(exclude_none=True)