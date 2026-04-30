"""Endpoint para generar liquidaciones de sueldo."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.empleado import Empleado
from app.models.liquidacion import Liquidacion
from app.models.liquidacion_detalle import LiquidacionDetalle
from app.services.liquidacion_service import (
    ResultadoLiquidacion,
    corregir_liquidacion,
    generar_liquidacion,
    obtener_empleado_para_liquidacion,
    obtener_liquidacion_para_correccion,
)
from app.services.pdf_service import (
    generar_pdf_liquidacion,
    generar_pdf_liquidaciones_periodo,
    obtener_liquidacion_para_pdf,
)

router = APIRouter(prefix="/liquidaciones", tags=["liquidaciones"])


class LiquidacionGenerarRequest(BaseModel):
    """Datos necesarios para calcular una liquidacion."""

    empleado_id: int
    mes: int
    anio: int
    horas_feriado: Decimal = Decimal("0")
    horas_extra_extraordinarias: Decimal = Decimal("0")
    aplicar_asistencia_perfecta: bool = False
    descuento_cuenta_corriente: Decimal = Decimal("0")
    descuento_adelanto: Decimal = Decimal("0")
    descuento_varios: Decimal = Decimal("0")

    @field_validator("mes")
    @classmethod
    def validar_mes(cls, value: int) -> int:
        if value < 1 or value > 12:
            raise ValueError("El mes debe estar entre 1 y 12.")
        return value

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("El anio debe ser mayor que 0.")
        return value

    @field_validator(
        "horas_feriado",
        "horas_extra_extraordinarias",
        "descuento_cuenta_corriente",
        "descuento_adelanto",
        "descuento_varios",
    )
    @classmethod
    def validar_no_negativo(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("Este valor no puede ser negativo.")
        return value


class LiquidacionCorreccionRequest(BaseModel):
    """Datos editables para corregir una liquidacion histórica."""

    horas_extra_extraordinarias: Decimal = Decimal("0")
    horas_feriado: Decimal = Decimal("0")
    aplicar_asistencia_perfecta: bool = False
    descuento_cuenta_corriente: Decimal = Decimal("0")
    descuento_adelanto: Decimal = Decimal("0")
    descuento_varios: Decimal = Decimal("0")

    @field_validator(
        "horas_extra_extraordinarias",
        "horas_feriado",
        "descuento_cuenta_corriente",
        "descuento_adelanto",
        "descuento_varios",
    )
    @classmethod
    def validar_no_negativo(cls, value: Decimal) -> Decimal:
        """Impide horas o importes negativos en la corrección."""

        if value < 0:
            raise ValueError("Este valor no puede ser negativo.")
        return value


class LiquidacionDetalleResponse(BaseModel):
    """Representa un concepto guardado dentro del detalle."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    concepto: str
    tipo: str
    importe: Decimal
    orden: int


class LiquidacionResponse(BaseModel):
    """Respuesta completa con cabecera y detalles de la liquidacion."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    empleado_id: int
    mes: int
    anio: int
    horas_laborables_mes: Decimal
    horas_base_pagadas: Decimal
    horas_extra_automaticas: Decimal
    horas_extra_extraordinarias: Decimal
    horas_feriado: Decimal
    valor_hora_base: Decimal
    subtotal_horas: Decimal
    monto_feriado: Decimal
    asistencia_perfecta: Decimal
    total_descuentos: Decimal
    total_neto: Decimal
    total_en_letras: str
    fecha_generacion: datetime
    detalles: list[LiquidacionDetalleResponse]


class LiquidacionHistorialItemResponse(BaseModel):
    """Representa una fila resumida del historial de liquidaciones."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    empleado_id: int
    nombre_completo: str
    mes: int
    anio: int
    horas_laborables_mes: Decimal
    horas_base_pagadas: Decimal
    horas_extra_automaticas: Decimal
    horas_extra_extraordinarias: Decimal
    asistencia_perfecta: Decimal
    total_descuentos: Decimal
    total_neto: Decimal
    fecha_generacion: datetime


@router.get("/", response_model=list[LiquidacionHistorialItemResponse])
def get_liquidaciones(
    empleado_id: int | None = None,
    mes: int | None = None,
    anio: int | None = None,
    db: Session = Depends(get_db),
) -> list[LiquidacionHistorialItemResponse]:
    """Lista el historial resumido de liquidaciones generadas."""

    # Cargamos el empleado junto con cada liquidacion para poder construir el
    # nombre completo sin consultas adicionales. Si llegan filtros, los
    # aplicamos de forma incremental antes de ordenar por id descendente.
    stmt = (
        select(Liquidacion)
        .options(joinedload(Liquidacion.empleado))
    )

    if empleado_id is not None:
        stmt = stmt.where(Liquidacion.empleado_id == empleado_id)

    if mes is not None:
        stmt = stmt.where(Liquidacion.mes == mes)

    if anio is not None:
        stmt = stmt.where(Liquidacion.anio == anio)

    stmt = stmt.order_by(Liquidacion.id.desc())
    liquidaciones = list(db.scalars(stmt).all())

    # Transformamos los modelos ORM en una respuesta resumida pensada para el
    # historial del frontend.
    return [
        LiquidacionHistorialItemResponse(
            id=liquidacion.id,
            empleado_id=liquidacion.empleado_id,
            nombre_completo=(
                f"{liquidacion.empleado.nombre} {liquidacion.empleado.apellido}"
            ).strip(),
            mes=liquidacion.mes,
            anio=liquidacion.anio,
            horas_laborables_mes=liquidacion.horas_laborables_mes,
            horas_base_pagadas=liquidacion.horas_base_pagadas,
            horas_extra_automaticas=liquidacion.horas_extra_automaticas,
            horas_extra_extraordinarias=liquidacion.horas_extra_extraordinarias,
            asistencia_perfecta=liquidacion.asistencia_perfecta,
            total_descuentos=liquidacion.total_descuentos,
            total_neto=liquidacion.total_neto,
            fecha_generacion=liquidacion.fecha_generacion,
        )
        for liquidacion in liquidaciones
    ]


@router.get("/pdf-periodo")
def get_liquidaciones_pdf_periodo(
    mes: int,
    anio: int,
    empleado_id: int | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Genera un PDF con todas las liquidaciones de un período dado."""

    # Buscamos las liquidaciones del período con su empleado, categoría y
    # detalles para poder reutilizar el servicio de PDF sin consultas extra.
    stmt = (
        select(Liquidacion)
        .options(
            joinedload(Liquidacion.empleado).joinedload(Empleado.categoria),
            joinedload(Liquidacion.detalles),
        )
        .where(Liquidacion.mes == mes, Liquidacion.anio == anio)
    )

    if empleado_id is not None:
        stmt = stmt.where(Liquidacion.empleado_id == empleado_id)

    stmt = stmt.order_by(Liquidacion.id.desc())
    liquidaciones = list(db.scalars(stmt).unique().all())

    if not liquidaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay liquidaciones para el período indicado.",
        )

    pdf_bytes = generar_pdf_liquidaciones_periodo(liquidaciones)
    sufijo_empleado = f"_empleado_{empleado_id}" if empleado_id is not None else ""
    nombre_archivo = f"liquidaciones_{anio}_{mes:02d}{sufijo_empleado}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nombre_archivo}"'},
    )


@router.post(
    "/generar",
    response_model=LiquidacionResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_generar_liquidacion(
    payload: LiquidacionGenerarRequest,
    db: Session = Depends(get_db),
) -> LiquidacionResponse:
    """Genera y guarda una liquidacion de sueldo para un empleado."""

    empleado = obtener_empleado_para_liquidacion(db, payload.empleado_id)
    if empleado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El empleado indicado no existe.",
        )

    if empleado.categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El empleado no tiene una categoria asociada.",
        )

    resultado: ResultadoLiquidacion = generar_liquidacion(
        db=db,
        empleado=empleado,
        mes=payload.mes,
        anio=payload.anio,
        horas_feriado=payload.horas_feriado,
        horas_extra_extraordinarias=payload.horas_extra_extraordinarias,
        aplicar_asistencia_perfecta=payload.aplicar_asistencia_perfecta,
        descuento_cuenta_corriente=payload.descuento_cuenta_corriente,
        descuento_adelanto=payload.descuento_adelanto,
        descuento_varios=payload.descuento_varios,
    )

    liquidacion: Liquidacion = resultado.liquidacion
    detalles: list[LiquidacionDetalle] = resultado.detalles

    return LiquidacionResponse(
        id=liquidacion.id,
        empleado_id=liquidacion.empleado_id,
        mes=liquidacion.mes,
        anio=liquidacion.anio,
        horas_laborables_mes=liquidacion.horas_laborables_mes,
        horas_base_pagadas=liquidacion.horas_base_pagadas,
        horas_extra_automaticas=liquidacion.horas_extra_automaticas,
        horas_extra_extraordinarias=liquidacion.horas_extra_extraordinarias,
        horas_feriado=liquidacion.horas_feriado,
        valor_hora_base=liquidacion.valor_hora_base,
        subtotal_horas=liquidacion.subtotal_horas,
        monto_feriado=liquidacion.monto_feriado,
        asistencia_perfecta=liquidacion.asistencia_perfecta,
        total_descuentos=liquidacion.total_descuentos,
        total_neto=liquidacion.total_neto,
        total_en_letras=liquidacion.total_en_letras,
        fecha_generacion=liquidacion.fecha_generacion,
        detalles=detalles,
    )


@router.put("/{liquidacion_id}/corregir", response_model=LiquidacionResponse)
def put_corregir_liquidacion(
    liquidacion_id: int,
    payload: LiquidacionCorreccionRequest,
    db: Session = Depends(get_db),
) -> LiquidacionResponse:
    """Corrige una liquidacion histórica existente y regenera su detalle."""

    # Buscamos la liquidación con su empleado, categoría y detalles actuales
    # para poder recalcular sobre la base histórica ya almacenada.
    liquidacion = obtener_liquidacion_para_correccion(db, liquidacion_id)
    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La liquidacion indicada no existe.",
        )

    if liquidacion.empleado is None or liquidacion.empleado.categoria is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liquidacion no tiene empleado o categoria asociados.",
        )

    resultado: ResultadoLiquidacion = corregir_liquidacion(
        db=db,
        liquidacion=liquidacion,
        horas_extra_extraordinarias=payload.horas_extra_extraordinarias,
        horas_feriado=payload.horas_feriado,
        aplicar_asistencia_perfecta=payload.aplicar_asistencia_perfecta,
        descuento_cuenta_corriente=payload.descuento_cuenta_corriente,
        descuento_adelanto=payload.descuento_adelanto,
        descuento_varios=payload.descuento_varios,
    )

    liquidacion_corregida: Liquidacion = resultado.liquidacion
    detalles: list[LiquidacionDetalle] = resultado.detalles

    return LiquidacionResponse(
        id=liquidacion_corregida.id,
        empleado_id=liquidacion_corregida.empleado_id,
        mes=liquidacion_corregida.mes,
        anio=liquidacion_corregida.anio,
        horas_laborables_mes=liquidacion_corregida.horas_laborables_mes,
        horas_base_pagadas=liquidacion_corregida.horas_base_pagadas,
        horas_extra_automaticas=liquidacion_corregida.horas_extra_automaticas,
        horas_extra_extraordinarias=liquidacion_corregida.horas_extra_extraordinarias,
        horas_feriado=liquidacion_corregida.horas_feriado,
        valor_hora_base=liquidacion_corregida.valor_hora_base,
        subtotal_horas=liquidacion_corregida.subtotal_horas,
        monto_feriado=liquidacion_corregida.monto_feriado,
        asistencia_perfecta=liquidacion_corregida.asistencia_perfecta,
        total_descuentos=liquidacion_corregida.total_descuentos,
        total_neto=liquidacion_corregida.total_neto,
        total_en_letras=liquidacion_corregida.total_en_letras,
        fecha_generacion=liquidacion_corregida.fecha_generacion,
        detalles=detalles,
    )


@router.get("/{liquidacion_id}/pdf")
def get_liquidacion_pdf(
    liquidacion_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Genera y devuelve el PDF de una liquidacion existente."""

    liquidacion = obtener_liquidacion_para_pdf(db, liquidacion_id)
    if liquidacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La liquidacion indicada no existe.",
        )

    pdf_bytes = generar_pdf_liquidacion(liquidacion)
    nombre_archivo = f"liquidacion_{liquidacion.id}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nombre_archivo}"'},
    )
