"""Modelo de categoria para clasificar tipos de trabajo."""

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Categoria(Base):
    """Representa una categoria con su valor por hora."""

    __tablename__ = "categorias"

    # Identificador unico de la categoria dentro de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Nombre visible de la categoria. Es obligatorio para poder describirla.
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)

    # Valor monetario que se paga por cada hora trabajada en esta categoria.
    # Es obligatorio para poder calcular importes asociados.
    valor_hora: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
