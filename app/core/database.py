"""Configuracion de conexion y sesiones para SQLAlchemy 2.x."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL


# Creamos el engine, que es el objeto central encargado de administrar la
# comunicacion con la base de datos. Se apoya en la URL definida en la
# configuracion del proyecto.
engine = create_engine(DATABASE_URL)


# Definimos la fabrica de sesiones. Cada vez que la aplicacion necesite hablar
# con la base de datos, creara una sesion nueva a partir de este objeto.
# Desactivamos el refresco automatico al hacer commit para mantener un
# comportamiento predecible al trabajar con los modelos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Declaramos la clase base para todos los modelos ORM. Las tablas del proyecto
# deberian heredar de esta clase para que SQLAlchemy pueda registrarlas dentro
# del mismo metadata.
class Base(DeclarativeBase):
    """Base comun para los modelos ORM de la aplicacion."""


# Esta funcion entrega una sesion lista para usar y garantiza su cierre al
# terminar. Es util para integrarla con dependencias en frameworks como
# FastAPI, evitando dejar conexiones abiertas por accidente.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
