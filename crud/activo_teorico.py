from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schemas.activeTeoricoSchema import ActiveTeoricSchema
from models.active_teorico import ActiveTeorico

def get_active_teorico_by_code(db: Session, code: str):
    try:
        result = db.query(ActiveTeorico).filter(ActiveTeorico.bar_code == code).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activo teorico{e}")

def delete_all_data(db: Session):
    try:
        db.query(ActiveTeorico).delete()
        db.commit()
        return {"message": "All data deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting data: {e}")


def create(db: Session, activeTeorico: ActiveTeoricSchema):

    try:

        _activeTeorico = ActiveTeorico(
            bar_code=activeTeorico.bar_code,
            acquisition_date=activeTeorico.acquisition_date,
            description=activeTeorico.description,
            valor_adq=activeTeorico.valor_adq,
            valor_cont=activeTeorico.valor_cont
        )

        db.add(_activeTeorico)
        db.commit()
        db.refresh(_activeTeorico)

        return _activeTeorico

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando activo {e}")   
    