"""Logica de negocio para las operaciones de categorias."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria


def listar_categorias(db: Session) -> list[Categoria]:
    """Devuelve todas las categorias ordenadas por nombre."""

    # Construimos una consulta simple para obtener todas las categorias.
    # El orden por nombre ayuda a que la API responda de forma consistente.
    stmt = select(Categoria).order_by(Categoria.nombre)
    return list(db.scalars(stmt).all())


def crear_categoria(
    db: Session,
    nombre: str,
    valor_hora: Decimal,
    monto_asistencia_perfecta: Decimal,
) -> Categoria:
    """Crea una categoria nueva y la persiste en la base de datos."""

    # Instanciamos el modelo ORM con los datos ya validados por la capa API.
    categoria = Categoria(
        nombre=nombre,
        valor_hora=valor_hora,
        monto_asistencia_perfecta=monto_asistencia_perfecta,
    )

    # Guardamos la categoria, confirmamos la transaccion y refrescamos el
    # objeto para devolverlo con los datos finales generados por la base.
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def obtener_categoria_por_id(db: Session, categoria_id: int) -> Categoria | None:
    """Busca una categoria existente por su identificador."""

    # Esta consulta se reutiliza en la edicion para validar si el registro
    # existe antes de intentar modificarlo.
    stmt = select(Categoria).where(Categoria.id == categoria_id)
    return db.scalar(stmt)


def actualizar_categoria(
    db: Session,
    categoria: Categoria,
    valor_hora: Decimal,
    monto_asistencia_perfecta: Decimal,
) -> Categoria:
    """Actualiza los importes editables de una categoria existente."""

    # Solo modificamos los campos pedidos para esta fase: valor hora y monto
    # de asistencia perfecta. El nombre queda intacto.
    categoria.valor_hora = valor_hora
    categoria.monto_asistencia_perfecta = monto_asistencia_perfecta

    db.commit()
    db.refresh(categoria)
    return categoria
