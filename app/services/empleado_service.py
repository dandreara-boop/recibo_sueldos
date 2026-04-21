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
