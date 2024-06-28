from typing import TypeVar, Optional
from pydantic import BaseModel
from schemas.categorySchema import CategorySchema
from datetime import date
from fastapi import UploadFile, File

T = TypeVar('T')

class ArticleSchema(BaseModel):
    name: str = None
    description: Optional[str] = None
    code : str
    photo: Optional[str] = None
    category_id: int = None
    company_id: int = None

class ArticleEditSchema(BaseModel):
    name: str = None
    description: Optional[str] = None
    code: str
    photo: Optional[str] = None
    #company_id: int = None
    category_id: int = None

class ArticleSchemaWithCategory(BaseModel):
    name: str = None
    description: Optional[str] = None
    code : str
    photo: Optional[str] = None
    creation_date: date
    category_id: int = None
    category: CategorySchema
    company_id: int = None
