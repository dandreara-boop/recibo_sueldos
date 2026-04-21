"""Endpoint para generar liquidaciones de sueldo."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/liquidaciones", tags=["liquidaciones"])


class LiquidacionGenerarRequest(BaseModel):
    """Datos necesarios para calcular una liquidacion."""

    empleado_id: int
    mes: int
    anio: int
    horas_totales: Decimal
    horas_feriado: Decimal = Decimal("0")
    asistencia_perfecta: Decimal = Decimal("0")
    total_descuentos: Decimal = Decimal("0")

    @field_validator("mes")
    @classmethod
    def validar_mes(cls, value: int) -> int:
        """Valida que el mes este dentro del rango calendario."""

        if value < 1 or value > 12:
            raise ValueError("El mes debe estar entre 1 y 12.")
        return value

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, value: int) -> int:
        """Valida que el anio sea mayor que cero."""

        if value <= 0:
            raise ValueError("El anio debe ser mayor que 0.")
        return value

    @field_validator(
        "horas_totales",
        "horas_feriado",
        "asistencia_perfecta",
        "total_descuentos",
    )
    @classmethod
    def validar_no_negativo(cls, value: Decimal) -> Decimal:
        """Impide enviar numeros negativos en la liquidacion."""

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
    horas_totales:Decimal
    horas_normales: Decimal
    horas_extra: Decimal
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

    # Verificamos que el empleado exista y tenga categoria asociada, porque
    # sin esos datos no es posible calcular la liquidacion.
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
        horas_totales=payload.horas_totales,
        horas_feriado=payload.horas_feriado,
        asistencia_perfecta=payload.asistencia_perfecta,
        total_descuentos=payload.total_descuentos,
    )

    liquidacion: Liquidacion = resultado.liquidacion
    detalles: list[LiquidacionDetalle] = resultado.detalles

    # Construimos la respuesta de forma explicita para incluir el detalle ya
    # persistido junto con la cabecera principal.
    return LiquidacionResponse(
        id=liquidacion.id,
        empleado_id=liquidacion.empleado_id,
        mes=liquidacion.mes,
        anio=liquidacion.anio,
        horas_totales=liquidacion.horas_totales,
        horas_normales=liquidacion.horas_normales,
        horas_extra=liquidacion.horas_extra,
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
