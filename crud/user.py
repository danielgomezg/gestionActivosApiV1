from sqlalchemy.orm import Session
from schemas.userSchema import UserSchema
from models.user import Usuario
from fastapi import HTTPException, status

def get_user(db: Session, skip: int = 0, limit: int = 100):
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
