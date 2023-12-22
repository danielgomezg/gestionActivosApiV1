from sqlalchemy.orm import Session, joinedload
from schemas.profileSchema import ProfileSchema
from models.profile import Profile
from models.action import Action
from models.profile_action import ProfileAction
from fastapi import HTTPException, status


def get_profile_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        perfiles_con_acciones = (
            db.query(Profile)
            .outerjoin(ProfileAction, Profile.id == ProfileAction.profile_id)
            .outerjoin(Action, ProfileAction.action_id == Action.id)
            .options(joinedload(Profile.profileActions).joinedload(ProfileAction.action))
            .all()
        )
        #print(perfiles_con_acciones)
        resultados_limpios = []
        for perfil in perfiles_con_acciones:
            perfil_dict = perfil.__dict__
            acciones = [profile_action.action.__dict__ for profile_action in perfil.profileActions]
            for accion_dict in acciones:
                accion_dict.pop('_sa_instance_state', None)
            perfil_dict['profileActions'] = acciones
            resultados_limpios.append(perfil_dict)

        return resultados_limpios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener perfiles {e}")

def get_profile_by_id(db: Session, perfil_id: int):
    try:
        #result = db.query(Profile).filter(Profile.id == perfil_id).first()
        perfil_con_acciones = (
            db.query(Profile)
            .outerjoin(ProfileAction, Profile.id == ProfileAction.profile_id)
            .outerjoin(Action, ProfileAction.action_id == Action.id)
            .options(joinedload(Profile.profileActions).joinedload(ProfileAction.action))
            .filter(Profile.id == perfil_id)  # Filtrar por ID de perfil
            .all()
        )
        # Limpiar los resultados
        resultados_limpios = []
        for perfil in perfil_con_acciones:
            perfil_dict = perfil.__dict__
            acciones = [profile_action.action.__dict__ for profile_action in perfil.profileActions]
            for accion_dict in acciones:
                accion_dict.pop('_sa_instance_state', None)
            perfil_dict['profileActions'] = acciones
            resultados_limpios.append(perfil_dict)
        return resultados_limpios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar perfil {e}")


def create_profile(db: Session, perfil: ProfileSchema):
    try:
        _profile = Profile(
            name=perfil.name,
            description=perfil.description
        )

        db.add(_profile)
        db.commit()
        db.refresh(_profile)
        return _profile
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando perfil {e}")

def update_profile(db: Session, profile_id: int, name_edit: str, description_edit: str):
    try:
        profile_to_edit = db.query(Profile).filter(Profile.id == profile_id).first()
        if profile_to_edit:
            profile_to_edit.name = name_edit
            profile_to_edit.description = description_edit

            db.commit()
            profile = get_profile_by_id(db, profile_id)
            return profile
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando perfil: {e}")

def delete_profile(db: Session, profile_id: int):
    try:
        profile_to_delete = db.query(Profile).filter(Profile.id == profile_id).first()
        if profile_to_delete:
            db.delete(profile_to_delete)
            db.commit()
            return profile_id
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Perfil con id {profile_id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando perfil: {e}")