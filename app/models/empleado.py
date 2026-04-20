"""Modelo de empleado dentro del sistema."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.categoria import Categoria


class Empleado(Base):
    """Representa a una persona empleada dentro del sistema."""

    __tablename__ = "empleados"

    # Identificador unico del empleado dentro de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Nombre de pila del empleado. Es obligatorio para identificarlo.
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)

    # Apellido del empleado. Es obligatorio para completar su identificacion.
    apellido: Mapped[str] = mapped_column(String(255), nullable=False)

    # Documento nacional de identidad del empleado. Debe ser unico para evitar
    # registros duplicados dentro del sistema.
    dni: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Direccion declarada del empleado. Es obligatoria para conservar sus
    # datos personales basicos.
    domicilio: Mapped[str] = mapped_column(String(255), nullable=False)

    # Referencia a la categoria laboral del empleado. Este campo conecta el
    # registro con la tabla de categorias mediante una clave foranea.
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"),
        nullable=False,
    )

    # Indica si el empleado se encuentra activo en el sistema. Por defecto se
    # considera activo al momento de crear el registro.
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relacion ORM para acceder directamente a la categoria asociada al
    # empleado sin tener que consultar la clave foranea manualmente.
    #categoria: Mapped[Categoria] = relationship()
    categoria: Mapped[Categoria] = relationship(backref="empleados")
