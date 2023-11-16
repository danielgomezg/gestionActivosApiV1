from sqlalchemy.orm import Session
from helpers.schema import UserSchema
from models.user import Usuario


def get_user(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserSchema):
    _user = Usuario(
        name=user.name,
        email=user.email
    )

    db.add(_user)
    db.commit()
    db.refresh(_user)
    return _user