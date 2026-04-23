"""Modelo de categoria para clasificar tipos de trabajo."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Categoria(Base):
    """Representa una categoria con su valor por hora y asistencia perfecta."""

    __tablename__ = "categorias"

    # Identificador unico de la categoria dentro de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Nombre visible de la categoria. Es obligatorio para poder describirla.
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)

    # Valor monetario que se paga por cada hora trabajada en esta categoria.
    # Usamos Numeric para evitar errores de precision con importes.
    valor_hora: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Monto fijo de asistencia perfecta asociado a esta categoria.
    # Mas adelante, al liquidar, el sistema podra tomar este valor
    # automaticamente si corresponde aplicar asistencia perfecta.
    monto_asistencia_perfecta: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )