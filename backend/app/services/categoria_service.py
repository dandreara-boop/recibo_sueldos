"""Logica de negocio para las operaciones de categorias."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from decimal import Decimal



def listar_categorias(db: Session) -> list[Categoria]:
    """Devuelve todas las categorias ordenadas por nombre."""

    # Construimos una consulta simple para obtener todas las categorias.
    # El orden por nombre ayuda a que la API responda de forma consistente.
    stmt = select(Categoria).order_by(Categoria.nombre)
    return list(db.scalars(stmt).all())


def crear_categoria(db: Session, nombre: str, valor_hora: Decimal) -> Categoria:
    """Crea una categoria nueva y la persiste en la base de datos."""

    # Instanciamos el modelo ORM con los datos ya validados por la capa API.
    categoria = Categoria(nombre=nombre, valor_hora=valor_hora)

    # Guardamos la categoria, confirmamos la transaccion y refrescamos el
    # objeto para devolverlo con los datos finales generados por la base.
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria
