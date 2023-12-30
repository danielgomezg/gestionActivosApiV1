from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base



class Profile(Base):
    __tablename__ = 'perfil'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    removed = Column(Integer, default=0, nullable=False)

    # Relacion con usuario
    users = relationship('Usuario', back_populates='profile')
    #users = relationship('Usuario', back_populates='profile')

    # Relacion con sucursales
    profileActions = relationship('ProfileAction', back_populates='profile')


# from fastapi import FastAPI, Request

# app = FastAPI()

# async def my_middleware(request: Request, call_next):
#     # Accede a la ruta, el método HTTP y los encabezados de la solicitud
#     ruta = request.url.path
#     metodo = request.method
#     headers = request.headers

#     # si el metodo es post -> create
#     action = "create"

#     # si el path contiene sucursal
#     path = "sucursal"

#     # construimos la accion
#     action = action + '-' + path

#     # buscamos en la tabla intermedia si exite action con la id del pefil

    
#     # Código que se ejecutará antes de procesar la solicitud
#     print(f"Middleware: Antes de procesar la solicitud a la ruta {ruta} con el método {metodo}")
#     print(f"Encabezados de la solicitud: {headers}")
    
#     # Llama al siguiente middleware o a la ruta manejadora
#     return await call_next(request)
    
# # Registra el middleware en la aplicación
# app.add_middleware(my_middleware)

# # Rutas manejadoras de ejemplo
# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}
