import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship
from datetime import date, datetime
import pandas as pd
from schemas.activeSchema import ActiveSchema

class Active(Base):
    __tablename__ = 'activo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bar_code = Column(String, nullable=False)
    virtual_code = Column(String, nullable=True)
    comment= Column(String, nullable=True)
    acquisition_date = Column(Date, default=date.today, nullable=False)
    accounting_document = Column(String, nullable=False)
    accounting_record_number = Column(String, nullable=False)
    name_in_charge_active = Column(String, nullable=False)
    rut_in_charge_active = Column(String, nullable=False)
    serie = Column(String, nullable=False)
    model = Column(String, nullable=False)
    state = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    photo1 = Column(String, nullable=True)
    photo2 = Column(String, nullable=True)
    photo3 = Column(String, nullable=True)
    photo4 = Column(String, nullable=True)
    creation_date = Column(Date, default=date.today, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    #user_id = Column(Integer, ForeignKey('usuario.id'))
    #user = relationship('Usuario', back_populates='actives')

    office_id = Column(Integer, ForeignKey('oficina.id'))
    office = relationship('Office', back_populates='actives')

    article_id = Column(Integer, ForeignKey('articulo.id'))
    article = relationship('Article', back_populates='actives')

    # Relacion con historial
    historial = relationship('History', back_populates='active')


def validateActiveFromFile(active, articleId, officeId):

    try:
        # Aquí puedes acceder a los datos de cada fila
        codigo = '' if pd.isna(active.iloc[0]) else active.iloc[0] # OBLIGATORIO
        serie = '' if pd.isna(active.iloc[1]) else active.iloc[1] # OBLIGATORIO 
        model = '' if pd.isna(active.iloc[2]) else active.iloc[2] # OBLIGATORIO
        date = active.iloc[3]
        date = datetime.strptime(date, '%d-%m-%Y')
        # Convertir el objeto datetime de nuevo a una cadena, pero en el formato 'yyyy-mm-dd'
        date = date.strftime('%Y-%m-%d') # OBLIGATORIO

        state = '' if pd.isna(active.iloc[4]) else active.iloc[4] # OBLIGATORIO
        comment = '' if pd.isna(active.iloc[5]) else active.iloc[5]
        name_charge = '' if pd.isna(active.iloc[6]) else active.iloc[6] # OBLIGATORIO
        rut_charge = '' if pd.isna(active.iloc[7]) else active.iloc[7]  # OBLIGATORIO
        num_register = '' if pd.isna(active.iloc[8]) else active.iloc[8] # OBLIGATORIO

        new_active = {
            "bar_code": str(int(codigo)),
            "serie": str(serie),
            "model": str(model),
            "acquisition_date": date,
            "state": str(state),
            "comment": str(comment),
            "name_in_charge_active": str(name_charge),
            "rut_in_charge_active": str(rut_charge),
            "accounting_document": "",
            "accounting_record_number": str(num_register),
            "photo1": "",
            "photo2": "",
            "photo3": "",
            "photo4": "",
            "article_id": articleId,
            "office_id": officeId
        }

        if new_active["bar_code"] == '' or new_active["serie"] == '' or new_active["model"] == '' or new_active["state"] == '' or new_active["name_in_charge_active"] == '' or new_active["rut_in_charge_active"] == '':
            return None, "Faltan campos obligatorios"

        print(f"Active : {new_active}")
        new_active = ActiveSchema(**new_active)
        return new_active, "ok"
    
    except Exception as e:
        print(f"Error : {e}")
        print(f"Tipo de error : {type(e)}")
        print("Argumentos del error : ", e.args)
        return None, e