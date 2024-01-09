from sqlalchemy.orm import Session
from schemas.activeSchema import ActiveSchema, ActiveEditSchema
from models.active import Active
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import desc
import uuid
import shutil
from urllib.parse import urlparse
from pathlib import Path

def get_active_by_id(db: Session, active_id: int):
    try:
        result = db.query(Active).filter(Active.id == active_id).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activo {e}")

def get_active_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        return db.query(Active).filter(Active.removed == 0).offset(offset).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activo {e}")

def get_active_by_id_article(db: Session, article_id: int, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.article_id == article_id, Active.removed == 0).group_by(Active.id).order_by(desc(Active.id)).offset(offset).limit(limit).all()
        #print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_file_url(file: UploadFile, upload_folder: Path) -> str:
    try:
        unique_id = uuid.uuid4().hex
        # Concatena el UUID al nombre del archivo original
        filename_with_uuid = f"{unique_id}_{file.filename}"
        file_path = upload_folder / filename_with_uuid
        with open(file_path, "wb") as active_file:
            shutil.copyfileobj(file.file, active_file)

        # file_url = f"http://127.0.0.1:9000/files/files_active/{filename_with_uuid}"
        return filename_with_uuid
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar el documento de activo: {e}")

def create_active(db: Session, active: ActiveSchema):
    try:
        _active = Active(
            bar_code=active.bar_code,
            comment=active.comment,
            acquisition_date=active.acquisition_date,
            accounting_document = active.accounting_document,
            accounting_record_number=active.accounting_record_number,
            name_in_charge_active=active.name_in_charge_active,
            rut_in_charge_active=active.rut_in_charge_active,
            serie=active.serie,
            model=active.model,
            state=active.state,
            office_id=active.office_id,
            article_id=active.article_id
            #creation_date=article.creation_date,
        )

        db.add(_active)
        db.commit()
        db.refresh(_active)
        return _active
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando activo {e}")


def update_active(db: Session, active_id: int, active: ActiveEditSchema):
    try:
        active_to_edit = db.query(Active).filter(Active.id == active_id).first()
        if active_to_edit:
            active_to_edit.bar_code = active.bar_code
            active_to_edit.comment = active.comment
            active_to_edit.acquisition_date = active.acquisition_date
            active_to_edit.accounting_record_number = active.accounting_record_number
            active_to_edit.name_in_charge_active = active.name_in_charge_active
            active_to_edit.rut_in_charge_active = active.rut_in_charge_active
            active_to_edit.serie = active.serie
            active_to_edit.model = active.model
            active_to_edit.state = active.state
            active_to_edit.office_id = active.office_id

            #Se elimina el archivo reemplazado del servidor
            if (active_to_edit.accounting_document is not None and active.accounting_document is None):
                # Extraer el nombre del archivo de la URL
                # parsed_url = urlparse(active_to_edit.accounting_document)
                # filename = Path(parsed_url.path).name
                # Construir la ruta al archivo existente
                existing_file_path = Path("files") / "files_active" / active_to_edit.accounting_document

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.accounting_document = active.accounting_document

            db.commit()
            active = get_active_by_id(db, active_id)
            return active
            #return {"message": "Acción actualizada correctamente", "action": action_to_edit}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activo: {e}")

def delete_active(db: Session, active_id: int):
    try:
        active_to_delete = db.query(Active).filter(Active.id == active_id).first()
        if active_to_delete:
            active_to_delete.removed = 1
            db.commit()
            return active_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activo con id {active_id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando activo: {e}")
