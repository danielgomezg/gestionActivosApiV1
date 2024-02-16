# EJECUTAR PROYECTO EN MODO DEVELOPMENT

```
pip install --upgrade -r requirements.txt
``` 
```
uvicorn main:app --reload
```

# EJECUTAR DOCKER

## Crear imagen

* docker build -t gapi-i .

## Crear network

* docker network create gactivos

## Crear y ejecutar contenedor

* docker run --network=gactivos -d -p 8000:8000 --name gapi-c gapi-i
* docker run --network=gactivos -d --name gapi-c gapi-i

* docker create --network=gactivos --name gapi-c gapi-i


## Contenedor postgres

* docker run --network=gactivos -d -p 5432:5432 -e POSTGRES_PASSWORD=gactivos --name gbd-c postgres
* docker run --network=gactivos -d -e POSTGRES_PASSWORD=gactivos --name gbd-c postgres


## Crear BD en contenedor

* docker exec -it gbd-c psql -U postgres -c "CREATE DATABASE gestion_activos;"