from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schemas.activeTeoricoSchema import ActiveTeoricSchema
from models.active_teorico import ActiveTeorico

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
    