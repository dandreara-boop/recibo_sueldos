"""Endpoint para generar liquidaciones de sueldo."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.liquidacion import Liquidacion
from app.models.liquidacion_detalle import LiquidacionDetalle
from app.services.liquidacion_service import (
    ResultadoLiquidacion,
    generar_liquidacion,
    obtener_empleado_para_liquidacion,
)
from app.services.pdf_service import (
    generar_pdf_liquidacion,
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