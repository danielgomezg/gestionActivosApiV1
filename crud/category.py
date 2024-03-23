from sqlalchemy.orm import Session
from schemas.categorySchema import CategorySchema, CategoryEditSchema
from sqlalchemy import desc
from models.category import Category
from fastapi import HTTPException, status

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

        return categories
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar categorias {e}")

def get_categories_all_android(db: Session):
    return db.query(Category).filter(Category.removed == 0).all()

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
    
def get_category_by_parent_id(db: Session, parent_id: int, limit: int = 100, offset: int = 0):
    try:
        count = db.query(Category).filter(Category.parent_id == parent_id, Category.removed == 0).count()

        if count == 0:
            return count, []

        result = (
            db.query(Category)
            .filter(Category.parent_id == parent_id, Category.removed == 0)
            .order_by(desc(Category.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return count, result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al buscar compania {e}")

def create_category(db: Session, category: CategorySchema):
    try:
        _category = Category(
            #level=category.level,
            description=category.description,
            parent_id=category.parent_id
        )

        db.add(_category)
        db.commit()
        db.refresh(_category)

        return _category
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Error creando categoria {e}")

def update_category(db: Session, category_id: int, category: CategoryEditSchema):

    try:
        category_to_edit = db.query(Category).filter(Category.id == category_id).first()
        if category_to_edit:
            category_to_edit.description = category.description
            #category_to_edit.client_code = category.client_code

            db.commit()
            db.refresh(category_to_edit)

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

            return category_id
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria con id {category_id} no encontrada")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error eliminando categria: {e}")
    
def count_category_children(db: Session, category_id: int):
    try:
        return db.query(Category).filter(Category.parent_id == category_id, Category.removed == 0).count()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Error al contar las categorias hijas {e}")