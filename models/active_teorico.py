from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from schemas.activeTeoricoSchema import ActiveTeoricSchema

class ActiveTeorico(Base):
    __tablename__ = 'activo_teorico'
    id = Column(Integer, primary_key=True)
    bar_code = Column(String, nullable=False)
    acquisition_date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    valor_adq = Column(String, nullable=False)
    valor_cont = Column(String, nullable=False)


def validateActiveTeoricoFile(active):
    try:
        bar_code = active.iloc[0]
        acquisition_date = active.iloc[1]
        description = active.iloc[2]
        valor_adq = active.iloc[3]
        valor_cont = active.iloc[4]

        print(f"bar_code : {bar_code}")
        print(f"acquisition_date : {acquisition_date}")
        print(f"description : {description}")
        print(f"valor_adq : {valor_adq}")
        print(f"valor_cont : {valor_cont}")
        

        active_teorico = {
            "bar_code": str(int(bar_code)),
            "acquisition_date": str(acquisition_date),
            "description": str(description),
            "valor_adq": str(valor_adq),
            "valor_cont": str(valor_cont)
        }

        if active_teorico["bar_code"] == '':
            return None, "Faltan campos obligatorios"

        active_teorico = ActiveTeoricSchema(**active_teorico)
        return active_teorico, "ok"

    except Exception as e:
        print(f"Error : {e}")
        print(f"Tipo de error : {type(e)}")
        print("Argumentos del error : ", e.args)
        return None, e