from sqlalchemy.orm import Session, joinedload
from schemas.userSchema import UserSchema, UserEditSchema
from models.user import Usuario
from fastapi import HTTPException, status, Depends

#login
from datetime import datetime, timedelta
from jose import jwt
from decouple import config

#impornaciones current user
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Tuple
from jose import jwt, JWTError

#Variables
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

def get_user_by_id(db: Session, user_id: int):
    try:
        result = db.query(Usuario).filter(Usuario.id == user_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar usuario {e}")

#funciones
def get_user_email(db: Session, email: str):
    result = db.query(Usuario).filter(Usuario.email == email).first()
    #print(result)
    return result


def get_user_all(db: Session, skip: int = 0, limit: int = 100):
    #return db.query(Usuario).offset(skip).limit(limit).all()
    return (db.query(Usuario).options(joinedload(Usuario.profile)).offset(skip).limit(limit).all())

def create_user(db: Session, user: UserSchema):
    try:
        _user = Usuario(
            firstName=user.firstName,
            secondName = user.secondName,
            lastName = user.lastName,
            secondLastName = user.secondLastName,
            email=user.email,
            password = user.password,
            rut = user.rut,
            company_id= user.company_id,
            profile_id= user.profile_id
        )

        db.add(_user)
        db.commit()
        db.refresh(_user)
        return _user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando user {e}")

def update_user(db: Session, user_id: int, user: UserEditSchema):
    user_to_edit = db.query(Usuario).filter(Usuario.id == user_id).first()
    try:
        if user_to_edit:
            user_to_edit.firstName = user.firstName
            user_to_edit.secondName = user.secondName
            user_to_edit.lastName = user.lastName
            user_to_edit.secondLastName = user.secondLastName
            user_to_edit.mail = user.email
            user_to_edit.password = user.password

            db.commit()
            action = get_user_by_id(db, user_id)
            return action
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acción no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando acción: {e}")

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
        expire = (datetime.utcnow() + expires_delta).timestamp()

    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer("/token")

#Obtener usuario actual con el token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales no validas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        #id_user:str = payload.get("sub")
        id_user = payload.get("sub")

        # Obtener el tiempo de expiración (exp) del token
        expiration_time = payload['exp']

        if id_user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    #Recoradr que es str
    return id_user, expiration_time

def get_user_disable_current(current_user_info: Tuple[str, Optional[str]] = Depends(get_current_user)):
    # Obtener la fecha y hora actual
    current_time = datetime.utcnow().timestamp()
    id_user, expiration_time = current_user_info
    # Validar si el token ha expirado
    if int(expiration_time) > int(current_time):
        print("El token no ha expirado aún.")
        return id_user, expiration_time
    else:
        print("El token ha expirado.")
        return (None, None)