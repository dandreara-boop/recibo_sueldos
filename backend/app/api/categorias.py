"""Endpoints y esquemas para el CRUD basico de categorias."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.categoria import Categoria
from app.services.categoria_service import (
    actualizar_categoria,
    crear_categoria,
    listar_categorias,
    obtener_categoria_por_id,
)

router = APIRouter(prefix="/categorias", tags=["categorias"])


class CategoriaCreate(BaseModel):
    """Esquema de entrada para crear una categoria."""

    nombre: str
    valor_hora: Decimal
    monto_asistencia_perfecta: Decimal = Decimal("0")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        """Evita nombres vacios o compuestos solo por espacios."""

        # Limpiamos espacios laterales para aceptar entradas habituales sin
        # guardar separadores innecesarios en la base de datos.
        nombre_limpio = value.strip()
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacio.")
        return nombre_limpio

    @field_validator("valor_hora", "monto_asistencia_perfecta")
    @classmethod
    def validar_importes(cls, value: Decimal, info) -> Decimal:
        """
        Valida importes monetarios.

        - valor_hora debe ser mayor que 0
        - monto_asistencia_perfecta no puede ser negativo
        """

        if info.field_name == "valor_hora" and value <= 0:
            raise ValueError("El valor_hora debe ser mayor que 0.")

        if info.field_name == "monto_asistencia_perfecta" and value < 0:
            raise ValueError(
                "El monto_asistencia_perfecta no puede ser negativo."
            )

        return value


class CategoriaResponse(BaseModel):
    """Esquema de salida para exponer categorias en la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    valor_hora: Decimal
    monto_asistencia_perfecta: Decimal


class CategoriaUpdate(BaseModel):
    """Esquema de entrada para editar importes de una categoria."""

    valor_hora: Decimal
    monto_asistencia_perfecta: Decimal

    @field_validator("valor_hora")
    @classmethod
    def validar_valor_hora(cls, value: Decimal) -> Decimal:
        """Exige un valor por hora positivo."""

        if value <= 0:
            raise ValueError("El valor_hora debe ser mayor que 0.")
        return value

    @field_validator("monto_asistencia_perfecta")
    @classmethod
    def validar_asistencia(cls, value: Decimal) -> Decimal:
        """Impide importes negativos en asistencia perfecta."""

        if value < 0:
            raise ValueError(
                "El monto_asistencia_perfecta no puede ser negativo."
            )
        return value


@router.get("/", response_model=list[CategoriaResponse])
def get_categorias(db: Session = Depends(get_db)) -> list[Categoria]:
    """Lista todas las categorias disponibles."""

    # La sesion se inyecta con Depends para reutilizar la conexion configurada
    # en la capa central de la aplicacion.
    return listar_categorias(db)


@router.post(
    "/",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_categoria(
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db),
) -> Categoria:
    """Crea una nueva categoria a partir de los datos recibidos."""

    # La API delega la persistencia en el servicio para mantener separada la
    # validacion HTTP de la logica de negocio.
    return crear_categoria(
        db=db,
        nombre=categoria_data.nombre,
        valor_hora=categoria_data.valor_hora,
        monto_asistencia_perfecta=categoria_data.monto_asistencia_perfecta,
    )


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def put_categoria(
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    db: Session = Depends(get_db),
) -> Categoria:
    """Actualiza los importes editables de una categoria existente."""

    # Verificamos primero que la categoria exista para devolver un 404 claro
    # si el usuario intenta editar un registro inexistente.
    categoria = obtener_categoria_por_id(db, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoria indicada no existe.",
        )

    return actualizar_categoria(
        db=db,
        categoria=categoria,
        valor_hora=categoria_data.valor_hora,
        monto_asistencia_perfecta=categoria_data.monto_asistencia_perfecta,
    )
