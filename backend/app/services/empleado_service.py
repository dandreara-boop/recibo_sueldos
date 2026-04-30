"""Logica de negocio para las operaciones basicas de empleados."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.categoria import Categoria
from app.models.empleado import Empleado


def listar_empleados(db: Session) -> list[Empleado]:
    """Devuelve todos los empleados junto con su categoria asociada."""

    # Cargamos tambien la categoria para que la respuesta de la API pueda
    # incluir sus datos basicos sin disparar consultas adicionales.
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.categoria))
        .order_by(Empleado.apellido, Empleado.nombre)
    )
    return list(db.scalars(stmt).all())


def obtener_empleado_por_dni(db: Session, dni: str) -> Empleado | None:
    """Busca un empleado existente por su DNI."""

    # Esta consulta se usa para evitar duplicados antes de crear un registro.
    stmt = select(Empleado).where(Empleado.dni == dni)
    return db.scalar(stmt)


def obtener_empleado_por_id(db: Session, empleado_id: int) -> Empleado | None:
    """Busca un empleado por su identificador junto con su categoria."""

    # Cargamos la categoria en la misma consulta para poder devolver la
    # respuesta completa luego de editar el registro.
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.categoria))
        .where(Empleado.id == empleado_id)
    )
    return db.scalar(stmt)


def obtener_categoria_por_id(db: Session, categoria_id: int) -> Categoria | None:
    """Busca una categoria por su identificador."""

    # Verificamos que la categoria exista antes de asociarla al empleado.
    stmt = select(Categoria).where(Categoria.id == categoria_id)
    return db.scalar(stmt)


def crear_empleado(
    db: Session,
    nombre: str,
    apellido: str,
    dni: str,
    domicilio: str,
    categoria_id: int,
) -> Empleado:
    """Crea un empleado nuevo y devuelve el registro persistido."""

    # Creamos el objeto ORM con los datos ya validados por la capa API.
    empleado = Empleado(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        domicilio=domicilio,
        categoria_id=categoria_id,
    )

    # Persistimos el empleado y recargamos la categoria para devolver una
    # respuesta lista para serializar.
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


def actualizar_empleado(
    db: Session,
    empleado: Empleado,
    nombre: str,
    apellido: str,
    dni: str,
    domicilio: str,
    categoria_id: int,
    activo: bool,
) -> Empleado:
    """Actualiza un empleado existente y devuelve el registro persistido."""

    # Asignamos los nuevos datos ya validados por la capa API.
    empleado.nombre = nombre
    empleado.apellido = apellido
    empleado.dni = dni
    empleado.domicilio = domicilio
    empleado.categoria_id = categoria_id
    empleado.activo = activo

    db.commit()

    empleado_actualizado = obtener_empleado_por_id(db, empleado.id)
    return empleado_actualizado


def obtener_empleado_por_dni_excluyendo_id(
    db: Session,
    dni: str,
    empleado_id: int,
) -> Empleado | None:
    """Busca un empleado por DNI, excluyendo un empleado específico."""

    stmt = (
        select(Empleado)
        .where(Empleado.dni == dni)
        .where(Empleado.id != empleado_id)
    )
    return db.scalar(stmt)