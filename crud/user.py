from sqlalchemy.orm import Session
from schemas.userSchema import UserSchema
from models.user import Usuario
from fastapi import HTTPException, status

#login
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def get_user_email(db: Session, email: str):
    result = db.query(Usuario).filter(Usuario.email == email).first()
    #print(result)
    return result


def get_user_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserSchema):
    try:
        _user = Usuario(
            firstName=user.firstName,
            secondName = user.secondName,
            lastName = user.lastName,
            secondLastName = user.secondLastName,
            email=user.email,
            password = user.password,
            rut = user.rut
        )

        db.add(_user)
        db.commit()
        db.refresh(_user)
        return _user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando user {e}")

def authenticate_user(email: str, password: str, db: Session):
    print(email)
    print(password)
    userExist = get_user_email(db, email)
    if(userExist):
        # print(userExist.password)
        passwordValid = Usuario.verify_password(password, userExist.password)
        if(passwordValid):
            print("exito")
            return userExist
        else:
            return False
    return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt