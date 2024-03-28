from fastapi import APIRouter, Depends, Header
from database import get_db, conexion
from sqlalchemy.orm import Session
from schemas.schemaGenerico import Response
from crud.user import get_user_disable_current
from typing import Tuple
from datetime import timedelta
from fastapi.responses import JSONResponse

from crud.company import get_company_by_id, get_company_by_rut
from crud.sucursal import get_sucursales_all_android
from crud.office import get_offices_all_android
from crud.active import get_actives_all_android
from crud.article import get_articles_all_android
from crud.category import get_categories_all_android
from crud.user import create_access_token, authenticate_user

from schemas.userSchema import UserSchemaLoginAndroid

router = APIRouter()

@router.get("/all/data")
def all_data(db: Session = Depends(get_db), current_user_info: Tuple[str, str] = Depends(get_user_disable_current), companyId: int = Header(None)):
    name_user, expiration_time = current_user_info

    db = next(conexion(db, companyId))
    if db is None:
        return Response(code="404", result=[], message="BD no encontrada").model_dump()

    # Se valida la expiracion del token
    if expiration_time is None:
        return Response(code="401", message="token-exp", result=[])

    print("antes")
    company = get_company_by_id(db, companyId)
    sucursales = get_sucursales_all_android(db)
    offices = get_offices_all_android(db)
    articles = get_articles_all_android(db)
    actives = get_actives_all_android(db)
    categories = get_categories_all_android(db)

    companies_data = {"id": company.id, "name": company.name,"rut": company.rut, "country": company.country,
                       "contact_name": company.contact_name, "contact_email": company.contact_email, "contact_phone": company.contact_phone,
                       "removed": company.removed, "name_db": company.name_db,}
    sucursales_data = [{"id": sucursal.id, "description": sucursal.description, "number": sucursal.number, "address": sucursal.address,
                        "region": sucursal.region, "city": sucursal.city, "commune": sucursal.commune, "removed": sucursal.removed,
                        "company_id": sucursal.company_id} for sucursal in sucursales]
    offices_data = [{"id": office.id, "description":office.description, "floor": office.floor, "name_in_charge": office.name_in_charge,
                      "removed": office.removed, "sucursal_id":office.sucursal_id} for office in offices]
    articles_data =[{ "id": article.id, "name":article.name, "description":article.description, "code":article.code, "photo":article.photo,
                      "count_active":article.count_active, "creation_date": article.creation_date, "removed": article.removed,
                      "category_id":article.category_id, "company_id":article.company_id} for article in articles]
    actives_data =[{"id": active.id, "bar_code": active.bar_code, "comment": active.comment, "acquisition_date": active.acquisition_date,
                    "accounting_document": active.accounting_document, "accounting_record_number": active.accounting_record_number,
                    "name_in_charge_active": active.name_in_charge_active, "rut_in_charge_active": active.rut_in_charge_active, "serie": active.serie,
                    "model":active.model, "state": active.state, "creation_date": active.creation_date, "removed": active.removed,
                    "office_id": active.office_id, "article_id": active.article_id} for active in actives]
    categories_data = [{"id": category.id, "description": category.description, "parent_id": category.parent_id, "removed": category.removed} for category in categories]

    print("despues")
    data = {"company": companies_data, "sucursales": sucursales_data, "offices": offices_data, "articles":articles_data, "actives":actives_data, "categories":categories_data}
    #return {"company": companies_data, "sucursales": sucursales_data, "offices": offices_data, "articles":articles_data, "actives":actives_data, "categories":categories_data}
    return Response(code="200", message="", result=data).model_dump()

@router.post('/login/app/android')
def login_access_android(request: UserSchemaLoginAndroid, db: Session = Depends(get_db)):
    _user = authenticate_user(request.email, request.password, db)
    if (_user and _user.profile_id != 2):
        _company = get_company_by_rut(db, request.rutCompany)
        if(_company):
            access_token_expires = timedelta(minutes=300)
            user_id = str(_user.id)

            additional_info = {
                "email": _user.email,
                "firstName": _user.firstName,
                "lastName": _user.lastName,
                "secondName": _user.secondName,
                "secondLastName": _user.secondLastName,
                "rut": _user.rut,
                "profile_id": _user.profile_id,
                "company_id": _user.company_id,
                "id": _user.id
            }

            access_token = create_access_token(data={"sub": user_id, "profile": _user.profile_id, "company": _company.id, "user": additional_info},
                                               expires_delta=access_token_expires)

            expire_seconds = access_token_expires.total_seconds()

            return JSONResponse(
                content=Response(
                    code="201",
                    message="Usuario loggeado correctamente",
                    result={
                        "access_token": access_token,
                        "token_type": "bearer",
                        "expire_token": expire_seconds,
                        "user": additional_info,
                        "company_id": _company.id
                    },
                ).model_dump(),
                status_code=201,
            )
        else:
            return Response(code="401", message="No existe la compañia", result=[])
    else:
        return Response(code="401", message="Usuario incorrecto", result=[])

