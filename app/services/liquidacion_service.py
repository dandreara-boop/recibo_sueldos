"""Logica de negocio para generar liquidaciones de sueldo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.empleado import Empleado
from app.models.liquidacion import Liquidacion
from app.models.liquidacion_detalle import LiquidacionDetalle

HORAS_NORMALES_LIMITE = Decimal("208")
DECIMAL_CENTAVOS = Decimal("0.01")


@dataclass
class ResultadoLiquidacion:
    """Contiene la liquidacion generada junto con sus detalles."""

    liquidacion: Liquidacion
    detalles: list[LiquidacionDetalle]


def _to_decimal(value: Decimal | float | int) -> Decimal:
    """Convierte un valor numerico a Decimal con dos decimales."""

    # Normalizamos todos los calculos monetarios para evitar errores de
    # precision propios de los flotantes.
    return Decimal(str(value)).quantize(DECIMAL_CENTAVOS, rounding=ROUND_HALF_UP)


def obtener_empleado_para_liquidacion(db: Session, empleado_id: int) -> Empleado | None:
    """Busca un empleado con su categoria para poder liquidarlo."""

    # Cargamos la categoria en la misma consulta porque el valor hora base
    # depende directamente de esa relacion.
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.categoria))
        .where(Empleado.id == empleado_id)
    )
    return db.scalar(stmt)


def generar_liquidacion(
    db: Session,
    empleado: Empleado,
    mes: int,
    anio: int,
    horas_totales: Decimal,
    horas_feriado: Decimal,
    asistencia_perfecta: Decimal,
    total_descuentos: Decimal,
) -> ResultadoLiquidacion:
    """Calcula y guarda una liquidacion junto con sus detalles."""

    # Tomamos el valor hora desde la categoria vigente del empleado y lo
    # convertimos a Decimal para mantener precision monetaria.
    valor_hora_base = _to_decimal(empleado.categoria.valor_hora)

    # Las horas normales se pagan hasta un maximo de 208. El excedente se
    # considera hora extra.
    horas_normales = min(horas_totales, HORAS_NORMALES_LIMITE)
    horas_extra = max(horas_totales - HORAS_NORMALES_LIMITE, Decimal("0"))

    # Calculamos cada componente salarial por separado para luego armar tanto
    # el resumen principal como el detalle de conceptos.
    monto_horas_normales = _to_decimal(horas_normales * valor_hora_base)
    monto_horas_extra = _to_decimal(horas_extra * valor_hora_base * Decimal("2"))
    subtotal_horas = _to_decimal(monto_horas_normales + monto_horas_extra)

    # Las horas de feriado se liquidan como un adicional independiente.
    monto_feriado = _to_decimal(horas_feriado * valor_hora_base)

    # El total neto surge de sumar haberes y restar descuentos.
    total_neto = _to_decimal(
        subtotal_horas + monto_feriado + asistencia_perfecta - total_descuentos
    )

    # Guardamos un texto simple que deja trazabilidad del importe final.
    total_en_letras = f"Total neto: {total_neto}"

    liquidacion = Liquidacion(
        empleado_id=empleado.id,
        mes=mes,
        anio=anio,
        horas_totales=float(horas_totales),
        horas_normales=float(horas_normales),
        horas_extra=float(horas_extra),
        horas_feriado=float(horas_feriado),
        valor_hora_base=valor_hora_base,
        subtotal_horas=subtotal_horas,
        monto_feriado=monto_feriado,
        asistencia_perfecta=asistencia_perfecta,
        total_descuentos=total_descuentos,
        total_neto=total_neto,
        total_en_letras=total_en_letras,
        fecha_generacion=datetime.utcnow(),
    )

    # Armamos solo los conceptos que realmente aportan valor a la liquidacion
    # para que el detalle sea claro y facil de leer.
    detalles: list[LiquidacionDetalle] = []
    orden = 1

    if monto_horas_normales > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas normales",
                tipo="haber",
                importe=monto_horas_normales,
                orden=orden,
            )
        )
        orden += 1

    if monto_horas_extra > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas extra al doble",
                tipo="haber",
                importe=monto_horas_extra,
                orden=orden,
            )
        )
        orden += 1

    if monto_feriado > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Adicional por feriado",
                tipo="haber",
                importe=monto_feriado,
                orden=orden,
            )
        )
        orden += 1

    if asistencia_perfecta > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Asistencia perfecta",
                tipo="haber",
                importe=asistencia_perfecta,
                orden=orden,
            )
        )
        orden += 1

    if total_descuentos > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Descuentos",
                tipo="descuento",
                importe=total_descuentos,
                orden=orden,
            )
        )

    # Persistimos primero la liquidacion principal para obtener su id y luego
    # vinculamos los detalles dentro de la misma transaccion.
    db.add(liquidacion)
    db.flush()

    for detalle in detalles:
        detalle.liquidacion_id = liquidacion.id
        db.add(detalle)

    db.commit()
    db.refresh(liquidacion)

    for detalle in detalles:
        db.refresh(detalle)

    return ResultadoLiquidacion(liquidacion=liquidacion, detalles=detalles)
