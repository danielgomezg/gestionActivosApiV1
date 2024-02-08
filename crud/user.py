from sqlalchemy.orm import Session, joinedload, load_only
from schemas.userSchema import UserSchema, UserEditSchema
from models.user import Usuario
from fastapi import HTTPException, status, Depends
from sqlalchemy import func

#login
from datetime import datetime, timedelta
from jose import jwt
from decouple import config

#impornaciones current user
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Tuple
from jose import jwt, JWTError

from passlib.hash import bcrypt

#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history

#Variables
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

def get_user_by_id(db: Session, user_id: int):
    try:
        result = db.query(Usuario).filter(Usuario.id == user_id).options(load_only(Usuario.id, Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName, Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar usuario {e}")

#funciones
def get_user_email(db: Session, email: str):
    try:
        result = db.query(Usuario).filter(Usuario.email == email).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener user por email {e}")


def get_user_all(db: Session, limit: int = 100, offset: int = 0):
    #return db.query(Usuario).offset(offset).limit(limit).all()
    try:
        result = (db.query(Usuario).options(joinedload(Usuario.profile)).filter(Usuario.removed == 0).offset(offset).limit(limit).all())

        count = db.query(Usuario).filter(Usuario.removed == 0).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener usuarios {e}")

def search_users_by_mail_rut(db: Session, search: str, limit: int = 100, offset: int = 0):
    try:
        query =  (
                    db.query(Usuario).
                        filter(Usuario.removed == 0, 
                            (
                                func.lower(Usuario.rut).like(f"%{search}%") |
                                func.lower(Usuario.email).like(f"%{search}%") |
                                func.lower(Usuario.firstName).like(f"%{search}%") |
                                func.lower(Usuario.lastName).like(f"%{search}%") 
                            ))
                            .offset(offset).limit(limit))

        users = query.all()
        count = query.count()

        return users, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar Usuarios {e}")

def create_user(db: Session, user: UserSchema, id_user: int):
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

        # creacion del historial
        # history_params = {
        #     "description": "create-user",
        #     "user_id": _user.id,
        #     "company_id": _user.company_id,
        #     "current_session_user_id": id_user
        # }
        # create_history(db, HistorySchema(**history_params))

        return _user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando user {e}")

def update_user(db: Session, user_id: int, user: UserEditSchema, id_user: int):

    try:
        user_to_edit = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user_to_edit:
            if user.password is None:
                user_to_edit.firstName = user.firstName
                user_to_edit.secondName = user.secondName
                user_to_edit.lastName = user.lastName
                user_to_edit.secondLastName = user.secondLastName
                user_to_edit.email = user.email
                user_to_edit.company_id = user.company_id
                user_to_edit.profile_id = user.profile_id
            else:

                user_to_edit.firstName = user.firstName
                user_to_edit.secondName = user.secondName
                user_to_edit.lastName = user.lastName
                user_to_edit.secondLastName = user.secondLastName
                user_to_edit.email = user.email
                user_to_edit._password = bcrypt.hash(user.password)
                user_to_edit.company_id = user.company_id
                user_to_edit.profile_id = user.profile_id

            db.commit()
            result = { k: v for k,v in user_to_edit.__dict__.items() if(k != "_password") }

            # creacion del historial
            # history_params = {
            #     "description": "update-user",
            #     "user_id": user_to_edit.id,
            #     "company_id": user_to_edit.company_id,
            #     "current_session_user_id": id_user
            # }
            # create_history(db, HistorySchema(**history_params))

            return user_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando usuario: {e}")

def delete_user(db: Session, user_id: int, id_user: int):

    try:
        user_to_delete = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user_to_delete:
            user_to_delete.removed = 1
            db.commit()

            # creacion del historial
            # history_params = {
            #     "description": "delete-user",
            #     "user_id": user_to_delete.id,
            #     "company_id": user_to_delete.company_id,
            #     "current_session_user_id": id_user
            # }
            # create_history(db, HistorySchema(**history_params))

            return user_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ususario con id {user_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando usuario: {e}")

def authenticate_user(email: str, password: str, db: Session):
    try:
        userExist = get_user_email(db, email)
        if(userExist and userExist.removed == 0):
            passwordValid = Usuario.verify_password(password, userExist.password)
            if(passwordValid):
                return userExist
            else:
                return False
        return False
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al autenticar usuario {e}")

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
        additional_info = payload.get("user", {})
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