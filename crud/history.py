from sqlalchemy.orm import Session, joinedload, load_only
from schemas.historySchema import HistorySchema
from models.history import History
from fastapi import HTTPException, status
from sqlalchemy import func, and_, desc

from models.user import Usuario

def get_history_all(db: Session, limit: int = 100, offset: int = 0):
    #return db.query(Usuario).offset(offset).limit(limit).all()
    try:
        result = (db.query(History).offset(offset).limit(limit).all())
        count = db.query(History).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener el historial {e}")

def get_history_by_company(db: Session, company_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(History)
                  .options(joinedload(History.sucursal))
                  .options(joinedload(History.company))
                  .options(joinedload(History.article))
                  .options(joinedload(History.user))
                  .options(joinedload(History.office))
                  .filter(History.company_id == company_id)
                  .order_by(desc(History.id))
                  .offset(offset)
                  .limit(limit)
                  .all())
        # hacer que result.sucursal = sucursal
        result = [history.__dict__ for history in result]
        for history in result:
            #history['sucursal'] = history['sucursal'].__dict__
            #history['sucursal'].pop('_sa_instance_state', None)
            if history['sucursal'] is not None:
                history['sucursal'] = history['sucursal'].__dict__
                history['sucursal'].pop('_sa_instance_state', None)

            if history['company'] is not None:
                history['company'] = history['company'].__dict__
                history['company'].pop('_sa_instance_state', None)

            if history['article'] is not None:
                history['article'] = history['article'].__dict__
                history['article'].pop('_sa_instance_state', None)

            if history['office'] is not None:
                history['office'] = history['office'].__dict__
                history['office'].pop('_sa_instance_state', None)

            if history['user'] is not None:
                history['user'] = history['user'].__dict__
                history['user'].pop('_sa_instance_state', None)

            # Aquí haces el get del usuario y lo asignas a la clave 'current_user'
            # current_session_user = history.get('current_session_user_id')
            # if current_session_user:
            #     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).options(load_only(Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName, Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
            #     history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None

            history.pop('sucursal_id', None)
            history.pop('company_id', None)
            history.pop('article_id', None)
            history.pop('user_id', None)
            history.pop('office_id', None)
            #history.pop('current_session_user_id', None)

        count = db.query(History).filter(History.company_id == company_id).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de companias {e}")


def get_history_by_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(History)
                  .options(joinedload(History.sucursal))
                  .options(joinedload(History.company))
                  .options(joinedload(History.office))
                  .options(joinedload(History.user))
                  .filter(History.sucursal_id == sucursal_id)
                  .order_by(desc(History.id))
                  .offset(offset)
                  .limit(limit)
                  .all())

        result = [history.__dict__ for history in result]
        for history in result:
            if history['sucursal'] is not None:
                history['sucursal'] = history['sucursal'].__dict__
                history['sucursal'].pop('_sa_instance_state', None)

            if history['company'] is not None:
                history['company'] = history['company'].__dict__
                history['company'].pop('_sa_instance_state', None)

            if history['office'] is not None:
                history['office'] = history['office'].__dict__
                history['office'].pop('_sa_instance_state', None)

            if history['user'] is not None:
                history['user'] = history['user'].__dict__
                history['user'].pop('_sa_instance_state', None)

            # Get del usuario actual
            # current_session_user = history.get('current_session_user_id')
            # if current_session_user:
            #     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).options(load_only(Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName, Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
            #     history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None

            history.pop('sucursal_id', None)
            history.pop('company_id', None)
            history.pop('office_id', None)
            history.pop('user_id', None)
            #history.pop('current_session_user_id', None)

        count = db.query(History).filter(History.sucursal_id == sucursal_id).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de sucursales {e}")


def get_history_by_office(db: Session, office_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(History)
                  .options(joinedload(History.sucursal))
                  .options(joinedload(History.office))
                  .options(joinedload(History.active))
                  .options(joinedload(History.article))
                  .options(joinedload(History.user))
                  .filter(History.office_id == office_id)
                  .order_by(desc(History.id))
                  .offset(offset)
                  .limit(limit)
                  .all())

        result = [history.__dict__ for history in result]
        for history in result:
            if history['office'] is not None:
                history['office'] = history['office'].__dict__
                history['office'].pop('_sa_instance_state', None)

            if history['sucursal'] is not None:
                history['sucursal'] = history['sucursal'].__dict__
                history['sucursal'].pop('_sa_instance_state', None)

            if history['active'] is not None:
                history['active'] = history['active'].__dict__
                history['active'].pop('_sa_instance_state', None)

            if history['article'] is not None:
                history['article'] = history['article'].__dict__
                history['article'].pop('_sa_instance_state', None)

            if history['user'] is not None:
                history['user'] = history['user'].__dict__
                history['user'].pop('_sa_instance_state', None)

            # Get del usuario actual
            # current_session_user = history.get('current_session_user_id')
            # if current_session_user:
            #     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).options(load_only(Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName, Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
            #     history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None

            history.pop('sucursal_id', None)
            history.pop('active_id', None)
            history.pop('office_id', None)
            history.pop('article_id', None)
            history.pop('user_id', None)
            #history.pop('current_session_user_id', None)

        count = db.query(History).filter(History.office_id == office_id).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de oficinas {e}")


def get_history_by_article(db: Session, article_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(History)
                  .options(joinedload(History.article))
                  .options(joinedload(History.company))
                  .options(joinedload(History.office))
                  .options(joinedload(History.active))
                  .options(joinedload(History.user))
                  .filter(History.article_id == article_id)
                  .order_by(desc(History.id))
                  .offset(offset)
                  .limit(limit)
                  .all())

        result = [history.__dict__ for history in result]
        for history in result:
            if history['article'] is not None:
                history['article'] = history['article'].__dict__
                history['article'].pop('_sa_instance_state', None)

            if history['company'] is not None:
                history['company'] = history['company'].__dict__
                history['company'].pop('_sa_instance_state', None)

            if history['active'] is not None:
                history['active'] = history['active'].__dict__
                history['active'].pop('_sa_instance_state', None)

            if history['office'] is not None:
                history['office'] = history['office'].__dict__
                history['office'].pop('_sa_instance_state', None)

            if history['user'] is not None:
                history['user'] = history['user'].__dict__
                history['user'].pop('_sa_instance_state', None)

            # Get del usuario actual
            # current_session_user = history.get('current_session_user_id')
            # if current_session_user:
            #     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).options(
            #         load_only(Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName,
            #                   Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
            #     history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None

            history.pop('company_id', None)
            history.pop('active_id', None)
            history.pop('article_id', None)
            history.pop('office_id', None)
            history.pop('user_id', None)
            #history.pop('current_session_user_id', None)

        count = db.query(History).filter(History.article_id == article_id).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de articulos {e}")


def get_history_by_active(db: Session, active_id: int, limit: int = 100, offset: int = 0):
    try:
        result = (db.query(History)
                  .options(joinedload(History.office))
                  .options(joinedload(History.article))
                  .options(joinedload(History.active))
                  .options(joinedload(History.user))
                  .filter(History.active_id == active_id)
                  .order_by(desc(History.id))
                  .offset(offset)
                  .limit(limit)
                  .all())

        result = [history.__dict__ for history in result]
        for history in result:
            if history['office'] is not None:
                history['office'] = history['office'].__dict__
                history['office'].pop('_sa_instance_state', None)

            if history['article'] is not None:
                history['article'] = history['article'].__dict__
                history['article'].pop('_sa_instance_state', None)

            if history['active'] is not None:
                history['active'] = history['active'].__dict__
                history['active'].pop('_sa_instance_state', None)

            if history['user'] is not None:
                history['user'] = history['user'].__dict__
                history['user'].pop('_sa_instance_state', None)

            # Get del usuario actual
            # current_session_user = history.get('current_session_user_id')
            # if current_session_user:
            #     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).options(
            #         load_only(Usuario.email, Usuario.company_id, Usuario.firstName, Usuario.lastName,
            #                   Usuario.profile_id, Usuario.rut, Usuario.secondLastName, Usuario.secondName)).first()
            #     history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None

            history.pop('article_id', None)
            history.pop('active_id', None)
            history.pop('office_id', None)
            history.pop('user_id', None)
            #history.pop('current_session_user_id', None)

        count = db.query(History).filter(History.active_id == active_id).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de activos {e}")


# def get_history_by_user(db: Session, user_id: int, limit: int = 100, offset: int = 0):
#     try:
#         result = (db.query(History)
#                   .options(joinedload(History.user))
#                   .options(joinedload(History.company))
#                   .filter(History.user_id == user_id)
#                   .offset(offset)
#                   .limit(limit)
#                   .all())
#
#         result = [history.__dict__ for history in result]
#         for history in result:
#             print("inicio")
#             if history['user'] is not None:
#                 history['user'] = history['user'].__dict__
#                 history['user'].pop('_sa_instance_state', None)
#
#             if history['company'] is not None:
#                 history['company'] = history['company'].__dict__
#                 history['company'].pop('_sa_instance_state', None)
#
#             # Get del usuario actual
#             current_session_user = history.get('current_session_user_id')
#             print(current_session_user)
#             if current_session_user:
#                 print(current_session_user)
#                 try:
#                     current_session_user_result = db.query(Usuario).filter(Usuario.id == current_session_user).first()
#                     print(f"Consulta exitosa: {current_session_user_result}")
#                 except Exception as user_query_error:
#                     print(f"Error al obtener usuario actual: {user_query_error}")
#                     current_session_user_result = None
#
#                 print(f"Consulta exitosa 2: {current_session_user_result}")
#
#                 history['current_session_user'] = current_session_user_result.__dict__ if current_session_user_result else None
#             print(f"Consulta exitosa 3: {current_session_user_result}")
#             history.pop('company_id', None)
#             history.pop('user_id', None)
#             history.pop('current_session_user_id', None)
#
#         count = db.query(History).filter(History.user_id == user_id).count()
#         return result, count
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener historial de usuarios {e}")

def create_history(db: Session, history: HistorySchema):
    try:
        _history = History(
            description=history.description,
            company_id=history.company_id,
            sucursal_id=history.sucursal_id,
            office_id=history.office_id,
            article_id=history.article_id,
            active_id=history.active_id,
            user_id=history.user_id,
            #current_session_user_id=history.current_session_user_id
        )

        db.add(_history)
        db.commit()
        db.refresh(_history)
        return _history
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando historial {e}")