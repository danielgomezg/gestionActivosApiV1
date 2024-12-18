from sqlalchemy.orm import Session, joinedload
from schemas.activeSchema import ActiveSchema, ActiveEditSchema
from sqlalchemy import func, select
from models.active import Active
from fastapi import HTTPException, status, UploadFile
import uuid
import random
import shutil
import hashlib
from pathlib import Path
from models.office import Office
from models.sucursal import Sucursal
from models.article import Article
from models.activeGroup_active import Active_GroupActive
from datetime import date, datetime, timedelta
import traceback
from typing import List

#historial
from schemas.historySchema import HistorySchema
from crud.history import create_history

def get_active_all_codes(db: Session, skip: int = 0, limit: int = 100):
    try:
        subquery = db.query(Active_GroupActive.active_id).subquery()
        count = db.query(Active).filter(Active.removed == 0, Active.id.notin_(subquery)).count()
        result = db.query(Active.id, Active.bar_code, Active.virtual_code).filter(Active.removed == 0, Active.id.notin_(subquery)).all()
        # Convertir los objetos Active en diccionarios
        result_dict = [
            {
                "id": id,
                "bar_code": bar_code,
                "virtual_code": virtual_code
            }
            for id, bar_code, virtual_code in result
        ]
        return result_dict, count
    except Exception as e:
        return [], 0
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activeValues {e}")

def get_active_by_id(db: Session, active_id: int):
    try:
        result = db.query(Active).filter(Active.id == active_id).options(joinedload(Active.article)).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activo {e}")

def count_active(db: Session):
    try:
        return db.query(Active).filter(Active.removed == 0).count()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al contar los activos {e}")

def get_active_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.removed == 0).order_by(Active.bar_code.desc(), Active.virtual_code.desc()).offset(offset).limit(limit).all()
        # Ordena los resultados en Python
        sorted_result = sort_bar_codes_desc(result)
        return sorted_result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activo {e}")

def get_actives_all_android(db: Session):
    try:
        return db.query(Active).filter(Active.removed == 0).all()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activo {e}")

def search_active(db: Session, search: str, limit: int = 100, offset: int = 0):
    try:
        subquery = select(db.query(Active_GroupActive.active_id).subquery())

        count = db.query(Active). \
            filter(
            Active.removed == 0,
            Active.id.notin_(subquery),
            (
                    func.lower(Active.bar_code).like(f"%{search}%") |
                    func.lower(Active.virtual_code).like(f"%{search}%")
            )).count()

        if count == 0:
            return [], count

        query = db.query(Active). \
            filter(
            Active.removed == 0,
            Active.id.notin_(subquery),
            (
                func.lower(Active.bar_code).like(f"%{search}%") |
                func.lower(Active.virtual_code).like(f"%{search}%")
            )
        ).offset(offset).limit(limit).all()

        return query, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Error al buscar activos por codigo virtual y barcode {e}")

def get_active_by_barcode(db: Session, bar_code: str, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.bar_code == bar_code, Active.removed == 0).options(joinedload(Active.article)).offset(offset).limit(limit).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_active_by_barcode_id(db: Session, bar_code: str, id_current: int, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.bar_code == bar_code, Active.removed == 0, Active.id != id_current).options(joinedload(Active.article)).offset(offset).limit(limit).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_active_by_virtual_code(db: Session, virtual_code: str):
    try:
        result = db.query(Active).filter(Active.virtual_code == virtual_code, Active.removed == 0).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_active_by_id_article(db: Session, article_id: int, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.article_id == article_id, Active.removed == 0).options(joinedload(Active.article)).offset(offset).limit(limit).all()
        count = db.query(Active).filter(Active.article_id == article_id, Active.removed == 0).count()
        #print(result)
        return result , count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def count_active_by_offices(db: Session, office_ids: List[int]):
    try:
        count = db.query(Active).filter(Active.office_id.in_(office_ids), Active.removed == 0).count()
        return count
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al obtener activos {e}",
        )

def get_active_by_offices(db: Session, office_ids: List[int], limit: int = 100, offset: int = 0, adjust_limit: bool = False):
    try:
        if adjust_limit:
            count_articles = count_active_by_offices(db, office_ids)
            if count_articles > limit:
                limit = count_articles

        count = db.query(Active).filter(Active.office_id.in_(office_ids), Active.removed == 0).count()
        if count == 0:
            return [], count

        result = (
            db.query(Active)
            .filter(Active.office_id.in_(office_ids), Active.removed == 0)
            .options(joinedload(Active.article), joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company))
            .order_by(Active.bar_code.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Ordena los resultados en Python
        sorted_result = sort_bar_codes_desc(result)
        return sorted_result, count
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error al obtener activos {e}",
        )

def get_active_by_office(db: Session, office_id: int, limit: int = 100, offset: int = 0):
    try:
        result = db.query(Active).filter(Active.office_id == office_id, Active.removed == 0).options(joinedload(Active.office).joinedload((Office.sucursal))).offset(offset).limit(limit).all()
        count = db.query(Active).filter(Active.office_id == office_id, Active.removed == 0).count()
        return result, count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def count_active_by_sucursal(db: Session, sucursal_id: int):
    try:
        count = db.query(Active).join(Office).join(Sucursal).filter(Sucursal.id == sucursal_id, Active.removed == 0).count()
        return count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def sort_bar_codes(results):
    def key_func(item):
        bar_code = item.bar_code
        virtual_code = item.virtual_code



        # Si `bar_code` es None, estos elementos se ordenan al final, usando `virtual_code` como clave
        if bar_code == "":
            try:
                print("virtual_code " + virtual_code)
                # Intentar convertir `virtual_code` a un número
                return (1, int(virtual_code))
            except (ValueError, TypeError):
                # Si `virtual_code` no se puede convertir a número, se usa tal cual como un string
                return (1, virtual_code or "")

        # Si `bar_code` no es None, intenta convertirlo a un número y usarlo para ordenar
        try:
            print("bar_code " + bar_code)
            return (0, int(bar_code))
        except (ValueError, TypeError):
            # Si `bar_code` no es un número, usar el string original como clave
            return (0, bar_code or "")

    # Ordenar los resultados usando la clave personalizada
    return sorted(results, key=key_func, reverse=True)

def sort_bar_codes_desc(results):
    def key_func(item):
        bar_code = item.bar_code
        virtual_code = item.virtual_code

        # Si `bar_code` es None, estos elementos se ordenan al final, usando `virtual_code` como clave
        if bar_code == "":
            try:
                # Intentar convertir `virtual_code` a un número
                return (1, -int(virtual_code))  # Negativo para orden descendente
            except (ValueError, TypeError):
                # Si `virtual_code` no se puede convertir a número, se usa tal cual como un string
                return (1, virtual_code or "")

        # Si `bar_code` no es None, intenta convertirlo a un número y usarlo para ordenar
        try:
            return (0, -int(bar_code))  # Negativo para orden descendente
        except (ValueError, TypeError):
            # Si `bar_code` no es un número, usar el string original como clave
            return (0, bar_code or "")

    # Ordenar los resultados usando la clave personalizada
    return sorted(results, key=key_func)

def get_active_by_sucursal(db: Session, sucursal_id: int, limit: int = 100, offset: int = 0, adjust_limit: bool = False):
    try:
        if adjust_limit:
            count_articles = count_active_by_sucursal(db, sucursal_id)
            if count_articles > limit:
                limit = count_articles

        count = db.query(Active).join(Office).join(Sucursal).filter(Sucursal.id == sucursal_id, Active.removed == 0).count()
        if count == 0:
            return [], count

        result = (db.query(Active).\
            join(Office).join(Sucursal).\
            filter(Sucursal.id == sucursal_id, Active.removed == 0).\
            options(joinedload(Active.article).joinedload(Article.category), joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company))
                  .order_by(Active.bar_code.desc()).offset(offset).limit(limit).all())

        # Ordena los resultados en Python
        sorted_result = sort_bar_codes_desc(result)
        return sorted_result, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def count_active_by_company(db: Session):
    try:
        count = db.query(Active).filter( Active.removed == 0).count()
        return count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def get_active_by_company(db: Session, limit: int = 100, offset: int = 0, adjust_limit: bool = False):
    try:
        if adjust_limit:
            count_actives = count_active_by_company(db)
            if count_actives > limit:
                limit = count_actives

        count = count_active_by_company(db)
        if count == 0:
            return [], count

        result = (db.query(Active). \
                  join(Office).join(Sucursal). \
                  filter(Active.removed == 0). \
                  options(joinedload(Active.article).joinedload(Article.category),
                          joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company))
                  .order_by(Office.sucursal_id).offset(offset).limit(limit).all())


        return result, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al obtener activos {e}")

def search_active_all(db: Session, search: str, limit: int = 100, offset: int = 0):
    try:
        count = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Active.removed == 0,
            (
                func.lower(Active.bar_code).like(f"%{search}%") |
                func.lower(Active.virtual_code).like(f"%{search}%") |
                func.lower(Active.model).like(f"%{search}%") |
                func.lower(Active.serie).like(f"%{search}%") |
                func.lower(Active.parent_code).like(f"%{search}%") |
                func.lower(Active.brand).like(f"%{search}%")
            )).count()

        if count == 0:
            return [], count

        query = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Active.removed == 0,
            (
                func.lower(Active.bar_code).like(f"%{search}%") |
                func.lower(Active.virtual_code).like(f"%{search}%") |
                func.lower(Active.model).like(f"%{search}%") |
                func.lower(Active.serie).like(f"%{search}%") |
                func.lower(Active.parent_code).like(f"%{search}%") |
                func.lower(Active.brand).like(f"%{search}%")
            )
        ).options(joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company)
                  ).order_by(Active.bar_code.desc()).offset(offset).limit(limit)

        actives = query.all()

        return actives, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Error al buscar activos por sucursal por nombre {e}")

def search_active_sucursal(db: Session, search: str, sucursal_id: int, limit: int = 100, offset: int = 0):
    try:
        count = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Sucursal.id == sucursal_id,
            Active.removed == 0,
            (
                    func.lower(Active.bar_code).like(f"%{search}%") |
                    func.lower(Active.model).like(f"%{search}%") |
                    func.lower(Active.serie).like(f"%{search}%") |
                    func.lower(Active.accounting_record_number).like(f"%{search}%") |
                    func.lower(Active.brand).like(f"%{search}%")
            )).count()
        
        if count == 0:
            return [], count

        query = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Sucursal.id == sucursal_id,
            Active.removed == 0,
            (
                    func.lower(Active.bar_code).like(f"%{search}%") |
                    func.lower(Active.model).like(f"%{search}%") |
                    func.lower(Active.serie).like(f"%{search}%") |
                    func.lower(Active.accounting_record_number).like(f"%{search}%") |
                    func.lower(Active.brand).like(f"%{search}%")
            )
            ).options(joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company)
            ).order_by(Active.office_id).offset(offset).limit(limit)

        actives = query.all()

        return actives, count
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activos por sucursal por nombre {e}")

def search_active_offices(db: Session, search: str, office_ids: List[int], limit: int = 100, offset: int = 0):
    try:

        count = db.query(Active). \
            filter(
            Active.office_id.in_(office_ids),
            Active.removed == 0,
            (
                    func.lower(Active.bar_code).like(f"%{search}%") |
                    func.lower(Active.model).like(f"%{search}%") |
                    func.lower(Active.serie).like(f"%{search}%") |
                    func.lower(Active.accounting_record_number).like(f"%{search}%") |
                    func.lower(Active.brand).like(f"%{search}%")
            )
            ).count()
    
        if count == 0:
            return [], count

        query = db.query(Active). \
            filter(
            Active.office_id.in_(office_ids),
            Active.removed == 0,
            (
                    func.lower(Active.bar_code).like(f"%{search}%") |
                    func.lower(Active.model).like(f"%{search}%") |
                    func.lower(Active.serie).like(f"%{search}%") |
                    func.lower(Active.accounting_record_number).like(f"%{search}%") |
                    func.lower(Active.brand).like(f"%{search}%")
            )
            ).options(joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company)
            ).order_by(Active.office_id).offset(offset).limit(limit)

        actives = query.all()

        return actives, count
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar activos por oficinas por nombre {e}")

def search_active_article(db: Session, search: str, article_id: int, limit: int = 100, offset: int = 0):
    try:
        count = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Active.article_id == article_id,
            Active.removed == 0,
            (
                func.lower(Active.bar_code).like(f"%{search}%") |
                func.lower(Active.virtual_code).like(f"%{search}%") |
                func.lower(Active.model).like(f"%{search}%") |
                func.lower(Active.serie).like(f"%{search}%") |
                func.lower(Active.parent_code).like(f"%{search}%") |
                func.lower(Active.brand).like(f"%{search}%")
            )).count()

        if count == 0:
            return [], count

        query = db.query(Active). \
            join(Office).join(Sucursal). \
            filter(
            Active.article_id == article_id,
            Active.removed == 0,
            (
                func.lower(Active.bar_code).like(f"%{search}%") |
                func.lower(Active.virtual_code).like(f"%{search}%") |
                func.lower(Active.model).like(f"%{search}%") |
                func.lower(Active.serie).like(f"%{search}%") |
                func.lower(Active.parent_code).like(f"%{search}%") |
                func.lower(Active.brand).like(f"%{search}%")
            )
        ).options(joinedload(Active.office).joinedload(Office.sucursal).joinedload(Sucursal.company)
                  ).order_by(Active.bar_code.desc()).offset(offset).limit(limit)

        actives = query.all()

        return actives, count

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Error al buscar activos por sucursal por nombre {e}")

def generate_short_unique_id(data: str, length: int = 20) -> str:
    # Generar un número aleatorio
    random_number = random.randint(0, 1000000000)  # Un entero grande
    # Combinar el string de entrada con el número aleatorio
    data_with_random = data + str(random_number)
    hash_object = hashlib.sha256(data_with_random.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:length]

def get_file_url(file: UploadFile, upload_folder: Path) -> str:
    try:
        unique_id = uuid.uuid4().hex
        # Concatena el UUID al nombre del archivo original
        filename_with_uuid = f"{unique_id}_{file.filename}"
        file_path = upload_folder / filename_with_uuid
        with open(file_path, "wb") as active_file:
            shutil.copyfileobj(file.file, active_file)

        return filename_with_uuid
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar el documento de activo: {e}")

def get_image_url(file: UploadFile, upload_folder: Path) -> str:
    try:
        unique_id = generate_short_unique_id(file.filename)
        # Concatena el UUID al nombre del archivo original
        filename_with_uuid = f"{unique_id}_{file.filename}"
        file_path = upload_folder / filename_with_uuid
        with open(file_path, "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)
        return filename_with_uuid
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar la imagen: {e}")

def create_active(db: Session, active: ActiveSchema, name_user: str):
    try:
        _active = Active(
            bar_code=active.bar_code,
            virtual_code=active.virtual_code,
            comment=active.comment,
            acquisition_date=active.acquisition_date,
            accounting_document = active.accounting_document,
            accounting_record_number=active.accounting_record_number,
            name_in_charge_active=active.name_in_charge_active,
            rut_in_charge_active=active.rut_in_charge_active,
            serie=active.serie,
            model=active.model,
            state=active.state,
            brand=active.brand,
            photo1=active.photo1,
            photo2=active.photo2,
            photo3=active.photo3,
            photo4=active.photo4,
            office_id=active.office_id,
            article_id=active.article_id,
            maintenance_ref=active.acquisition_date,
            maintenance_days=active.maintenance_days,
            parent_code = active.parent_code
        )
        db.add(_active)
        db.commit()
        db.refresh(_active)

        active_content = get_active_by_id(db, _active.id)
        id_company = active_content.article.company_id

        # creacion del historial
        history_params = {
            "description": "create-active",
            "active_id": _active.id,
            "article_id": _active.article_id,
            "office_id": _active.office_id,
            "name_user": name_user,
            "company_id": id_company
        }

        create_history(db, HistorySchema(**history_params))
        return _active
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando activo {e}")

def update_active(db: Session, active_id: int, active: ActiveEditSchema, name_user: str):
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
            active_to_edit.brand = active.brand
            active_to_edit.office_id = active.office_id
            active_to_edit.maintenance_days = active.maintenance_days
            active_to_edit.parent_code = active.parent_code

            #Se elimina el archivo reemplazado del servidor
            if len(active_to_edit.accounting_document) > 0 and active_to_edit.accounting_document != active.accounting_document:
                existing_file_path = Path("files") / "files_active" / active_to_edit.accounting_document

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.accounting_document = active.accounting_document

            # Se elimina la foto reemplazada del servidor
            # Si la foto es nula, no se hace nada
            if active_to_edit.photo1 is not None and active_to_edit.photo1 != "" and active_to_edit.photo1 != active.photo1:
                existing_file_path = Path("files") / "images_active" / active_to_edit.photo1

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.photo1 = active.photo1


            if active_to_edit.photo2 is not None and active_to_edit.photo2 != "" and active_to_edit.photo2 != active.photo2:
                existing_file_path = Path("files") / "images_active" / active_to_edit.photo2

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.photo2 = active.photo2

            if active_to_edit.photo3 is not None and active_to_edit.photo3 != "" and active_to_edit.photo3 != active.photo3:
                existing_file_path = Path("files") / "images_active" / active_to_edit.photo3

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.photo3 = active.photo3

            if active_to_edit.photo4 is not None and active_to_edit.photo4 != "" and active_to_edit.photo4 != active.photo4:
                existing_file_path = Path("files") / "images_active" / active_to_edit.photo4

                # Verificar si el archivo existe y eliminarlo
                if existing_file_path.exists():
                    existing_file_path.unlink()

            active_to_edit.photo4 = active.photo4

            db.commit()

            active_content = get_active_by_id(db, active_to_edit.id)
            id_company = active_content.article.company_id

            # creacion del historial
            history_params = {
                "description": "update-active",
                "active_id": active_to_edit.id,
                "article_id": active_to_edit.article_id,
                "office_id": active_to_edit.office_id,
                "name_user": name_user,
                "company_id": id_company
            }
            create_history(db, HistorySchema(**history_params))

            return active_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activo: {e}")

def delete_active(db: Session, active_id: int, name_user: str):
    try:
        active_to_delete = db.query(Active).filter(Active.id == active_id).first()
        if active_to_delete:
            active_to_delete.removed = 1
            db.commit()

            active_content = get_active_by_id(db, active_to_delete.id)
            id_company = active_content.article.company_id

            # creacion del historial
            history_params = {
                "description": "delete-active",
                "active_id": active_to_delete.id,
                "article_id": active_to_delete.article_id,
                "office_id": active_to_delete.office_id,
                "name_user": name_user,
                "company_id": id_company
            }
            create_history(db, HistorySchema(**history_params))

            return active_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Activo con id {active_id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando activo: {e}")

def update_maintenance_ref(db: Session, active_id: int, maintenance_ref: date):
    try:
        active_to_edit = db.query(Active).filter(Active.id == active_id).first()
        if active_to_edit:
            active_to_edit.maintenance_ref = maintenance_ref
            db.commit()
            db.refresh(active_to_edit)
            return active_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activo: {e}")

#Actualiza la fecha de mantenimiento; parametro updates es una lista de activos
def update_maintenance_refs(db: Session, updates: list):
    try:
        for active_id, maintenance_ref in updates:
            active_to_edit = db.query(Active).filter(Active.id == active_id).first()
            if active_to_edit:
                active_to_edit.maintenance_ref = maintenance_ref
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activos: {e}")

#NO SE USA
def maintenance_days_remaining2(db: Session, actives):
    updates = []
    for active in actives:
        print("----", active.id)
        if active.maintenance_ref and active.maintenance_days:
            days_since_last_maintenance = (datetime.now().date() - active.maintenance_ref).days
            print("days_since_last_maintenance ", days_since_last_maintenance)
            active.maintenance_days_remaining = active.maintenance_days - days_since_last_maintenance
            print("maintenance_days_remaining ", active.maintenance_days_remaining)

            # Si el tiempo de mantenimiento ha pasado, se establece maintenance_ref a la fecha ref anterior mas los dias de mantenimiento
            if active.maintenance_days_remaining < 0:
                _maintenance_ref = active.maintenance_ref + timedelta(days=active.maintenance_days)
                print("_maintenance_ref ", _maintenance_ref)
                updates.append((active.id, _maintenance_ref))

                #_active_up = update_maintenance_ref(db, active.id, _maintenance_ref)
                #active = _active_up

    # Aplicar todas las actualizaciones en una sola transacción
    if updates:
        update_maintenance_refs(db, updates)

        # Refrescar los objetos en memoria con los nuevos valores de mantenimiento
        for active in actives:
            for update in updates:
                if active.id == update[0]:
                    active.maintenance_ref = update[1]
                    days_since_last_maintenance = (datetime.now().date() - active.maintenance_ref).days
                    active.maintenance_days_remaining = active.maintenance_days - days_since_last_maintenance

    return actives


def maintenance_days_remaining(actives):
    for active in actives:
        print("----", active.id)
        if active.maintenance_ref and active.maintenance_days:
            days_since_last_maintenance = (datetime.now().date() - active.maintenance_ref).days
            print("days_since_last_maintenance ", days_since_last_maintenance)

            # Calcular los días restantes de mantenimiento
            remaining_days = active.maintenance_days - days_since_last_maintenance
            print("remaining_days ", remaining_days)

            # Si el tiempo de mantenimiento ha pasado o es el día de mantenimiento, establecer a 0
            if remaining_days <= 0:
                active.maintenance_days_remaining = 0
            else:
                active.maintenance_days_remaining = remaining_days

            print("maintenance_days_remaining ", active.maintenance_days_remaining)

    return actives

def update_maintenance_active(db: Session, active_id: int, name_user: str):
    try:
        active_to_edit = db.query(Active).filter(Active.id == active_id).first()

        if active_to_edit:
            _maintenance_ref = datetime.now().date() + timedelta(days=active_to_edit.maintenance_days)
            active_to_edit.maintenance_ref = _maintenance_ref

            db.commit()

            active_content = get_active_by_id(db, active_to_edit.id)
            id_company = active_content.article.company_id

            # creacion del historial
            history_params = {
                "description": "update-active",
                "active_id": active_to_edit.id,
                "article_id": active_to_edit.article_id,
                "office_id": active_to_edit.office_id,
                "name_user": name_user,
                "company_id": id_company
            }
            create_history(db, HistorySchema(**history_params))

            return active_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando activo: {e}")