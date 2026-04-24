"""Modelo de liquidacion mensual de haberes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.empleado import Empleado


class Liquidacion(Base):
    """Representa una liquidacion salarial asociada a un empleado."""

    __tablename__ = "liquidaciones"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Empleado al que pertenece la liquidacion.
    empleado_id: Mapped[int] = mapped_column(
        ForeignKey("empleados.id"),
        nullable=False,
    )

    # Periodo liquidado.
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cantidad de horas laborables reales del mes segun calendario
    # (lunes a sabado, 8 horas por dia). Este dato es informativo.
    horas_laborables_mes: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Horas base pagadas. En este sistema se pagan 208 horas siempre.
    horas_base_pagadas: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Horas extra automaticas. En esta nueva logica, como no se cargan
    # horas trabajadas manuales, quedan en 0 salvo que mas adelante
    # se incorpore una fuente automatica de horas reales.
    horas_extra_automaticas: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    # Horas extra extraordinarias cargadas manualmente.
    horas_extra_extraordinarias: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    # Horas trabajadas en feriado.
    horas_feriado: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    # Valor hora base de la categoria.
    valor_hora_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Subtotal correspondiente a horas base + horas extra.
    subtotal_horas: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Importe adicional por horas trabajadas en feriado.
    monto_feriado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Monto por asistencia perfecta.
    asistencia_perfecta: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    # Total de descuentos.
    total_descuentos: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    # Neto final.
    total_neto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Texto legal completo.
    total_en_letras: Mapped[str] = mapped_column(String(500), nullable=False)

    # Fecha de generacion.
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    empleado: Mapped[Empleado] = relationship(backref="liquidaciones")