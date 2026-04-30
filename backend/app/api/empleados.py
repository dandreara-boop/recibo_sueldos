"""Endpoints y esquemas para el CRUD basico de empleados."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.empleado import Empleado
from app.services.empleado_service import (
    actualizar_empleado,
    crear_empleado,
    listar_empleados,
    obtener_categoria_por_id,
    obtener_empleado_por_dni,
    obtener_empleado_por_id,
    obtener_empleado_por_dni_excluyendo_id,
)

router = APIRouter(prefix="/empleados", tags=["empleados"])


class EmpleadoCreate(BaseModel):
    """Esquema de entrada para crear un empleado."""

    nombre: str
    apellido: str
    dni: str
    domicilio: str
    categoria_id: int

    @field_validator("nombre", "apellido", "dni", "domicilio")
    @classmethod
    def validar_texto_no_vacio(cls, value: str) -> str:
        """Evita cadenas vacias o compuestas solo por espacios."""

        # Limpiamos espacios laterales para guardar datos consistentes y evitar
        # registros con texto vacio aparente.
        texto_limpio = value.strip()
        if not texto_limpio:
            raise ValueError("Este campo no puede estar vacio.")
        return texto_limpio


class CategoriaBasicaResponse(BaseModel):
    """Esquema reducido para exponer la categoria asociada."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    valor_hora: Decimal


class EmpleadoResponse(BaseModel):
    """Esquema de salida para devolver empleados con su categoria."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    dni: str
    domicilio: str
    activo: bool
    categoria_id: int
    categoria: CategoriaBasicaResponse


class EmpleadoUpdate(BaseModel):
    """Esquema de entrada para editar un empleado existente."""

    nombre: str
    apellido: str
    dni: str
    domicilio: str
    categoria_id: int
    activo: bool

    @field_validator("nombre", "apellido", "dni", "domicilio")
    @classmethod
    def validar_texto_no_vacio(cls, value: str) -> str:
        """Evita cadenas vacias o compuestas solo por espacios."""

        texto_limpio = value.strip()
        if not texto_limpio:
            raise ValueError("Este campo no puede estar vacio.")
        return texto_limpio


@router.get("/", response_model=list[EmpleadoResponse])
def get_empleados(db: Session = Depends(get_db)) -> list[EmpleadoResponse]:
    """Lista todos los empleados registrados."""

    # Reutilizamos la sesion inyectada por FastAPI para consultar la base y
    # devolver tambien la categoria asociada de cada empleado.
    return listar_empleados(db)


@router.post(
    "/",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_empleado(
    empleado_data: EmpleadoCreate,
    db: Session = Depends(get_db),
) -> EmpleadoResponse:
    """Crea un empleado luego de validar sus restricciones de negocio."""

    # Confirmamos que la categoria exista antes de intentar guardar el
    # empleado, para evitar una referencia invalida.
    categoria = obtener_categoria_por_id(db, empleado_data.categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoria indicada no existe.",
        )

    # Verificamos que el DNI no haya sido usado por otro empleado.
    empleado_existente = obtener_empleado_por_dni(db, empleado_data.dni)
    if empleado_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un empleado con ese DNI.",
        )
    

    # Delegamos la persistencia en el servicio para mantener la logica de
    # negocio separada de la capa HTTP.
    return crear_empleado(
        db=db,
        nombre=empleado_data.nombre,
        apellido=empleado_data.apellido,
        dni=empleado_data.dni,
        domicilio=empleado_data.domicilio,
        categoria_id=empleado_data.categoria_id,
    )


@router.put("/{empleado_id}", response_model=EmpleadoResponse)
def put_empleado(
    empleado_id: int,
    empleado_data: EmpleadoUpdate,
    db: Session = Depends(get_db),
) -> EmpleadoResponse:
    """Actualiza un empleado luego de validar sus restricciones de negocio."""

    # Confirmamos que el empleado exista antes de intentar editarlo.
    empleado = obtener_empleado_por_id(db, empleado_id)
    if empleado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El empleado indicado no existe.",
        )

    # Verificamos que la categoria elegida exista.
    categoria = obtener_categoria_por_id(db, empleado_data.categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoria indicada no existe.",
        )

    # Revisamos que el DNI no pertenezca a otro empleado distinto al actual.
    empleado_con_mismo_dni = obtener_empleado_por_dni_excluyendo_id(
        db=db,
        dni=empleado_data.dni,
        empleado_id=empleado_id,
    )

    if empleado_con_mismo_dni is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro empleado con ese DNI.",
        )

    return actualizar_empleado(
        db=db,
        empleado=empleado,
        nombre=empleado_data.nombre,
        apellido=empleado_data.apellido,
        dni=empleado_data.dni,
        domicilio=empleado_data.domicilio,
        categoria_id=empleado_data.categoria_id,
        activo=empleado_data.activo,
    )
