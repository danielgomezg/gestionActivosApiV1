from sqlalchemy.orm import Session, joinedload, join
from schemas.categorySchema import CategorySchema, CategoryEditSchema
from sqlalchemy import desc, func, and_
from models.category import Category
# from models.company import Company
# from models.sucursal import Sucursal
# from models.office import Office
from fastapi import HTTPException, status
#historial
# from schemas.historySchema import HistorySchema
# from crud.history import create_history


def get_category_all(db: Session, limit: int = 100, offset: int = 0):
    try:
        categories = (
            db.query(Category)
            .filter(Category.removed == 0)
            .group_by(Category.id)
            .order_by(desc(Category.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        # result = []
        # for company in companies:
        #     company[0].count_sucursal = company[1]
        #     result.append(company[0])

        return categories
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar categorias {e}")

def count_category(db: Session):
    try:
        return db.query(Category).filter(Category.removed == 0).count()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al contar las categorias {e}")

def get_category_by_id(db: Session, category_id: int):
    try:
        result = db.query(Category).filter(Category.id == category_id, Category.removed == 0).first()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania {e}")

def create_category(db: Session, category: CategorySchema):
    try:
        _category = Category(
            level=category.level,
            description=category.description,
            father_id=category.father_id,
            client_code=category.client_code
        )

        db.add(_category)
        db.commit()
        db.refresh(_category)
        #_company.count_sucursal = 0

        # creacion del historial
        # history_params = {
        #     "description": "create-company",
        #     "company_id": _company.id,
        #     "user_id": id_user
        # }
        #create_history(db, HistorySchema(**history_params))

        return _category
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando categoria {e}")

def update_category(db: Session, category_id: int, category: CategoryEditSchema):

    try:
        category_to_edit = db.query(Category).filter(Category.id == category_id).first()
        if category_to_edit:
            category_to_edit.description = category.description
            category_to_edit.client_code = category.client_code

            db.commit()
            db.refresh(category_to_edit)

            # creacion del historial
            # history_params = {
            #     "description": "update-company",
            #     "company_id": company_to_edit.id,
            #     "user_id": id_user
            #     #"current_session_user_id": id_user
            # }
            # create_history(db, HistorySchema(**history_params))

            return category_to_edit
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error editando categoria: {e}")

def delete_category(db: Session, category_id: int):
    try:
        category_to_delete = db.query(Category).filter(Category.id == category_id).first()
        if category_to_delete:
            category_to_delete.removed = 1
            db.commit()

            # creacion del historial
            # history_params = {
            #     "description": "delete-company",
            #     "company_id": company_id,
            #     "user_id": id_user
            #     #"current_session_user_id": id_user
            # }
            # create_history(db, HistorySchema(**history_params))

            return category_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria con id {category_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando categria: {e}")