"""Modelo de liquidacion mensual de haberes."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.empleado import Empleado
from decimal import Decimal



class Liquidacion(Base):
    """Representa una liquidacion salarial asociada a un empleado."""

    __tablename__ = "liquidaciones"

    # Identificador unico de la liquidacion dentro de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Referencia al empleado al que pertenece esta liquidacion. Se vincula con
    # la tabla de empleados mediante una clave foranea.
    empleado_id: Mapped[int] = mapped_column(
        ForeignKey("empleados.id"),
        nullable=False,
    )

    # Mes liquidado, representado como numero entero del 1 al 12.
    mes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Anio correspondiente al periodo liquidado.
    anio: Mapped[int] = mapped_column(Integer, nullable=False)

    # Total general de horas trabajadas en el periodo.
    horas_totales: Mapped[float] = mapped_column(Float, nullable=False)

    # Cantidad de horas normales trabajadas en el periodo.
    horas_normales: Mapped[float] = mapped_column(Float, nullable=False)

    # Cantidad de horas extra trabajadas en el periodo.
    horas_extra: Mapped[float] = mapped_column(Float, nullable=False)

    # Cantidad de horas trabajadas en dias feriados.
    horas_feriado: Mapped[float] = mapped_column(Float, nullable=False)

    # Valor base de la hora utilizado para calcular la liquidacion. Se guarda
    # como importe monetario usando precision decimal.
    valor_hora_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Suma parcial correspondiente al calculo de horas antes de adicionales y
    # descuentos.
    subtotal_horas: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Importe adicional generado por las horas trabajadas en feriado.
    monto_feriado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Monto adicional por asistencia perfecta. Por defecto comienza en cero si
    # no corresponde aplicar este concepto.
    asistencia_perfecta: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    # Total de descuentos aplicados a la liquidacion. Por defecto se inicializa
    # en cero hasta que existan descuentos a computar.
    total_descuentos: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    # Resultado final neto que percibe el empleado luego de sumar conceptos y
    # restar descuentos.
    total_neto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Representacion textual del total neto, util para recibos o reportes.
    total_en_letras: Mapped[str] = mapped_column(String(255), nullable=False)

    # Fecha y hora en la que se genero la liquidacion dentro del sistema.
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relacion ORM para acceder al empleado asociado sin consultar manualmente
    # la clave foranea.
    empleado: Mapped[Empleado] = relationship(backref="liquidaciones")
