"""Punto de entrada principal de la aplicacion FastAPI."""

from fastapi import FastAPI

from app.api.categorias import router as categorias_router
from app.api.empleados import router as empleados_router
from app.api.liquidaciones import router as liquidaciones_router
from app.core.init_db import init_db

app = FastAPI(title="Sueldos API")


@app.on_event("startup")
def on_startup() -> None:
    """Inicializa la base al arrancar la aplicacion."""

    # Creamos las tablas registradas antes de atender solicitudes para que el
    # CRUD de categorias pueda operar sobre una base lista para usar.
    init_db()


# Registramos el router de categorias para exponer los endpoints requeridos en
# esta fase inicial del backend.
app.include_router(categorias_router)
app.include_router(empleados_router)
app.include_router(liquidaciones_router)


@app.get("/")
def root():
    return {"mensaje": "API de sueldos funcionando correctamente"}
