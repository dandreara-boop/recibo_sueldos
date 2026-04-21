"""Utilidades para inicializar las tablas de la base de datos."""

from app.core.database import Base, engine
from app.models.categoria import Categoria
from app.models.empleado import Empleado
from app.models.liquidacion import Liquidacion
from app.models.liquidacion_detalle import LiquidacionDetalle


# Importamos todos los modelos para asegurarnos de que SQLAlchemy los registre
# en el metadata antes de intentar crear las tablas en la base de datos.
__all__ = [
    "Categoria",
    "Empleado",
    "Liquidacion",
    "LiquidacionDetalle",
    "init_db",
]


def init_db() -> None:
    """Crea todas las tablas definidas en los modelos registrados."""

    # Ejecutamos la creacion de tablas usando el metadata comun de la
    # aplicacion y el engine configurado para la conexion actual.
    Base.metadata.create_all(bind=engine)
