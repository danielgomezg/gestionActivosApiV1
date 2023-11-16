from fastapi import APIRouter
from models.company import company
from database import connection

router = APIRouter()

@router.get("/company")
def get_companies():
    return connection.execute(company.select()).fetchall()