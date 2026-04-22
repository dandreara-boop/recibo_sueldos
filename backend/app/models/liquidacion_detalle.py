"""Modelo de detalle para los conceptos de una liquidacion."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.liquidacion import Liquidacion


class LiquidacionDetalle(Base):
    """Representa una linea de detalle dentro de una liquidacion."""

    __tablename__ = "liquidaciones_detalle"

    # Identificador unico del detalle dentro de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Referencia a la liquidacion a la que pertenece este concepto. Se enlaza
    # con la tabla principal mediante una clave foranea.
    liquidacion_id: Mapped[int] = mapped_column(
        ForeignKey("liquidaciones.id"),
        nullable=False,
    )

    # Nombre o descripcion del concepto liquidado, por ejemplo un haber o un
    # descuento especifico.
    concepto: Mapped[str] = mapped_column(String(255), nullable=False)

    # Tipo de movimiento que representa el concepto. Los valores esperados son
    # "haber" o "descuento" para identificar su naturaleza.
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    # Importe monetario asociado al concepto. Se guarda con precision decimal
    # para evitar errores de redondeo en calculos financieros.
    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Posicion del concepto dentro del detalle de la liquidacion. Sirve para
    # conservar un orden de presentacion estable.
    orden: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relacion ORM para acceder directamente a la liquidacion asociada sin
    # consultar la clave foranea de forma manual.
    liquidacion: Mapped[Liquidacion] = relationship(backref="detalles")
