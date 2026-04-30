"""Logica de negocio para generar liquidaciones de sueldo."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models.empleado import Empleado
from app.models.liquidacion import Liquidacion
from app.models.liquidacion_detalle import LiquidacionDetalle

HORAS_BASE_MENSUALES = Decimal("208")
HORAS_POR_DIA = Decimal("8")
DECIMAL_CENTAVOS = Decimal("0.01")

UNIDADES = (
    "",
    "uno",
    "dos",
    "tres",
    "cuatro",
    "cinco",
    "seis",
    "siete",
    "ocho",
    "nueve",
)
DECENAS_ESPECIALES = {
    10: "diez",
    11: "once",
    12: "doce",
    13: "trece",
    14: "catorce",
    15: "quince",
    16: "dieciséis",
    17: "diecisiete",
    18: "dieciocho",
    19: "diecinueve",
    20: "veinte",
}
DECENAS = {
    2: "veinti",
    3: "treinta",
    4: "cuarenta",
    5: "cincuenta",
    6: "sesenta",
    7: "setenta",
    8: "ochenta",
    9: "noventa",
}
CENTENAS = {
    1: "ciento",
    2: "doscientos",
    3: "trescientos",
    4: "cuatrocientos",
    5: "quinientos",
    6: "seiscientos",
    7: "setecientos",
    8: "ochocientos",
    9: "novecientos",
}
MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


@dataclass
class ResultadoLiquidacion:
    """Contiene la liquidacion generada junto con sus detalles."""

    liquidacion: Liquidacion
    detalles: list[LiquidacionDetalle]


def _to_decimal(value: Decimal | float | int) -> Decimal:
    """Convierte un valor numerico a Decimal con dos decimales."""
    return Decimal(str(value)).quantize(DECIMAL_CENTAVOS, rounding=ROUND_HALF_UP)


def _calcular_horas_laborables_mes(mes: int, anio: int) -> Decimal:
    """
    Calcula las horas laborables del mes considerando:
    - lunes a sabado
    - 8 horas por dia
    """
    cantidad_dias_mes = calendar.monthrange(anio, mes)[1]
    dias_laborables = 0

    for dia in range(1, cantidad_dias_mes + 1):
        dia_semana = calendar.weekday(anio, mes, dia)
        # lunes=0 ... sabado=5, domingo=6
        if dia_semana <= 5:
            dias_laborables += 1

    return _to_decimal(Decimal(dias_laborables) * HORAS_POR_DIA)


def _numero_menor_a_mil_en_letras(numero: int) -> str:
    """Convierte un numero entero menor a mil a texto en espanol."""
    if numero == 0:
        return ""

    if numero == 100:
        return "cien"

    centenas = numero // 100
    resto = numero % 100
    partes: list[str] = []

    if centenas > 0:
        partes.append(CENTENAS[centenas])

    if resto in DECENAS_ESPECIALES:
        partes.append(DECENAS_ESPECIALES[resto])
    elif resto < 10:
        if resto > 0:
            partes.append(UNIDADES[resto])
    elif resto < 30:
        unidades = resto % 10
        if resto == 21:
            partes.append("veintiuno")
        else:
            partes.append(f"{DECENAS[2]}{UNIDADES[unidades]}")
    else:
        decena = resto // 10
        unidad = resto % 10
        texto_decena = DECENAS[decena]
        if unidad == 0:
            partes.append(texto_decena)
        else:
            partes.append(f"{texto_decena} y {UNIDADES[unidad]}")

    return " ".join(partes).strip()


def _numero_entero_en_letras(numero: int) -> str:
    """Convierte un entero no negativo a su representacion textual."""
    if numero == 0:
        return "cero"

    millones = numero // 1_000_000
    miles = (numero % 1_000_000) // 1_000
    resto = numero % 1_000
    partes: list[str] = []

    if millones > 0:
        if millones == 1:
            partes.append("un millón")
        else:
            partes.append(f"{_numero_entero_en_letras(millones)} millones")

    if miles > 0:
        if miles == 1:
            partes.append("mil")
        else:
            partes.append(f"{_numero_menor_a_mil_en_letras(miles)} mil")

    if resto > 0:
        partes.append(_numero_menor_a_mil_en_letras(resto))

    return " ".join(partes).strip()


def _monto_en_letras(monto: Decimal) -> str:
    """Convierte un importe monetario a texto legal con centavos."""
    monto_normalizado = _to_decimal(monto)
    parte_entera = int(monto_normalizado)
    centavos = int((monto_normalizado - Decimal(parte_entera)) * 100)
    texto_entero = _numero_entero_en_letras(parte_entera)

    if texto_entero.endswith(" veintiuno"):
        texto_entero = f"{texto_entero[:-9]} veintiún"
    elif texto_entero.endswith(" y uno"):
        texto_entero = f"{texto_entero[:-5]} y un"
    elif texto_entero.endswith(" uno"):
        texto_entero = f"{texto_entero[:-4]} un"
    elif texto_entero == "uno":
        texto_entero = "un"

    return f"{texto_entero} con {centavos:02d} centavos"


def _fecha_legal(fecha: datetime) -> str:
    """Devuelve la fecha en formato legal legible."""
    return f"{fecha.day} de {MESES[fecha.month]} de {fecha.year}"


def obtener_empleado_para_liquidacion(
    db: Session,
    empleado_id: int,
) -> Empleado | None:
    """Busca un empleado con su categoria para poder liquidarlo."""
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.categoria))
        .where(Empleado.id == empleado_id)
    )
    return db.scalar(stmt)


def obtener_liquidacion_para_correccion(
    db: Session,
    liquidacion_id: int,
) -> Liquidacion | None:
    """Busca una liquidacion existente con empleado, categoria y detalles."""

    # Cargamos todo lo necesario para recalcular y regenerar el detalle sin
    # depender de consultas perezosas posteriores.
    stmt = (
        select(Liquidacion)
        .options(
            joinedload(Liquidacion.empleado).joinedload(Empleado.categoria),
            joinedload(Liquidacion.detalles),
        )
        .where(Liquidacion.id == liquidacion_id)
    )
    return db.scalar(stmt)


def _construir_total_en_letras(
    empleado: Empleado,
    mes: int,
    anio: int,
    total_neto: Decimal,
    fecha_actual: datetime,
) -> str:
    """Construye el texto legal completo para la liquidacion."""

    nombre_completo = f"{empleado.nombre} {empleado.apellido}".strip()
    monto_en_letras = _monto_en_letras(total_neto)
    monto_en_numeros = format(total_neto, ".2f")
    periodo = f"{MESES.get(mes, '').capitalize()} de {anio}"

    return (
        f"El {_fecha_legal(fecha_actual)}, {nombre_completo} recibió de "
        f"M-50 S.A.S en concepto de pago correspondiente a {periodo} "
        f"la suma de pesos {monto_en_letras} ($ {monto_en_numeros})"
    )


def _construir_detalles_liquidacion(
    *,
    monto_horas_base: Decimal,
    monto_horas_extra_automaticas: Decimal,
    monto_horas_extra_extraordinarias: Decimal,
    monto_feriado: Decimal,
    asistencia_perfecta: Decimal,
    descuento_cuenta_corriente: Decimal,
    descuento_adelanto: Decimal,
    descuento_varios: Decimal,
) -> list[LiquidacionDetalle]:
    """Genera los conceptos de detalle consistentes para una liquidacion."""

    detalles: list[LiquidacionDetalle] = []
    orden = 1

    if monto_horas_base > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas base (mínimo garantizado 208 hs)",
                tipo="haber",
                importe=monto_horas_base,
                orden=orden,
            )
        )
        orden += 1

    if monto_horas_extra_automaticas > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas extra automáticas",
                tipo="haber",
                importe=monto_horas_extra_automaticas,
                orden=orden,
            )
        )
        orden += 1

    if monto_horas_extra_extraordinarias > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas extra extraordinarias",
                tipo="haber",
                importe=monto_horas_extra_extraordinarias,
                orden=orden,
            )
        )
        orden += 1

    if monto_feriado > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Horas trabajadas en feriado",
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

    if descuento_cuenta_corriente > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Cuenta corriente",
                tipo="descuento",
                importe=descuento_cuenta_corriente,
                orden=orden,
            )
        )
        orden += 1

    if descuento_adelanto > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Adelanto",
                tipo="descuento",
                importe=descuento_adelanto,
                orden=orden,
            )
        )
        orden += 1

    if descuento_varios > 0:
        detalles.append(
            LiquidacionDetalle(
                concepto="Varios",
                tipo="descuento",
                importe=descuento_varios,
                orden=orden,
            )
        )

    return detalles


def generar_liquidacion(
    db: Session,
    empleado: Empleado,
    mes: int,
    anio: int,
    horas_feriado: Decimal,
    horas_extra_extraordinarias: Decimal,
    aplicar_asistencia_perfecta: bool,
    descuento_cuenta_corriente: Decimal,
    descuento_adelanto: Decimal,
    descuento_varios: Decimal,
) -> ResultadoLiquidacion:
    """Calcula y guarda una liquidacion junto con sus detalles."""

    valor_hora_base = _to_decimal(empleado.categoria.valor_hora)

    # Horas informativas del calendario real del mes.
    horas_laborables_mes = _calcular_horas_laborables_mes(mes, anio)

    # En este sistema se pagan 208 horas base siempre.
    horas_base_pagadas = HORAS_BASE_MENSUALES

    # Por ahora no se cargan horas reales manuales, por lo tanto
    # no hay horas extra automaticas derivadas del exceso sobre 208.
    horas_extra_automaticas = max(
    horas_laborables_mes - HORAS_BASE_MENSUALES,
    Decimal("0.00"),
)

    horas_extra_extraordinarias = _to_decimal(horas_extra_extraordinarias)
    horas_feriado = _to_decimal(horas_feriado)

    monto_horas_base = _to_decimal(horas_base_pagadas * valor_hora_base)
    monto_horas_extra_automaticas = _to_decimal(
        horas_extra_automaticas * valor_hora_base * Decimal("2")
    )
    monto_horas_extra_extraordinarias = _to_decimal(
        horas_extra_extraordinarias * valor_hora_base * Decimal("2")
    )

    subtotal_horas = _to_decimal(
        monto_horas_base
        + monto_horas_extra_automaticas
        + monto_horas_extra_extraordinarias
    )

    monto_feriado = _to_decimal(horas_feriado * valor_hora_base)

    asistencia_perfecta = (
        _to_decimal(empleado.categoria.monto_asistencia_perfecta)
        if aplicar_asistencia_perfecta
        else Decimal("0.00")
    )

    total_descuentos = _to_decimal(
        descuento_cuenta_corriente
        + descuento_adelanto
        + descuento_varios
    )

    total_neto = _to_decimal(
        subtotal_horas + monto_feriado + asistencia_perfecta - total_descuentos
    )

    fecha_actual = datetime.now()
    total_en_letras = _construir_total_en_letras(
        empleado=empleado,
        mes=mes,
        anio=anio,
        total_neto=total_neto,
        fecha_actual=fecha_actual,
    )

    liquidacion = Liquidacion(
        empleado_id=empleado.id,
        mes=mes,
        anio=anio,
        horas_laborables_mes=horas_laborables_mes,
        horas_base_pagadas=horas_base_pagadas,
        horas_extra_automaticas=horas_extra_automaticas,
        horas_extra_extraordinarias=horas_extra_extraordinarias,
        horas_feriado=horas_feriado,
        valor_hora_base=valor_hora_base,
        subtotal_horas=subtotal_horas,
        monto_feriado=monto_feriado,
        asistencia_perfecta=asistencia_perfecta,
        total_descuentos=total_descuentos,
        total_neto=total_neto,
        total_en_letras=total_en_letras,
        fecha_generacion=fecha_actual,
    )

    detalles = _construir_detalles_liquidacion(
        monto_horas_base=monto_horas_base,
        monto_horas_extra_automaticas=monto_horas_extra_automaticas,
        monto_horas_extra_extraordinarias=monto_horas_extra_extraordinarias,
        monto_feriado=monto_feriado,
        asistencia_perfecta=asistencia_perfecta,
        descuento_cuenta_corriente=_to_decimal(descuento_cuenta_corriente),
        descuento_adelanto=_to_decimal(descuento_adelanto),
        descuento_varios=_to_decimal(descuento_varios),
    )

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


def corregir_liquidacion(
    db: Session,
    liquidacion: Liquidacion,
    horas_extra_extraordinarias: Decimal,
    horas_feriado: Decimal,
    aplicar_asistencia_perfecta: bool,
    descuento_cuenta_corriente: Decimal,
    descuento_adelanto: Decimal,
    descuento_varios: Decimal,
) -> ResultadoLiquidacion:
    """Corrige una liquidacion histórica sin alterar su contexto base."""

    # Reutilizamos el valor hora histórico guardado en la propia liquidación.
    valor_hora_base = _to_decimal(liquidacion.valor_hora_base)
    horas_base_pagadas = _to_decimal(liquidacion.horas_base_pagadas)
    horas_extra_automaticas = _to_decimal(liquidacion.horas_extra_automaticas)

    horas_extra_extraordinarias = _to_decimal(horas_extra_extraordinarias)
    horas_feriado = _to_decimal(horas_feriado)
    descuento_cuenta_corriente = _to_decimal(descuento_cuenta_corriente)
    descuento_adelanto = _to_decimal(descuento_adelanto)
    descuento_varios = _to_decimal(descuento_varios)

    monto_horas_base = _to_decimal(horas_base_pagadas * valor_hora_base)
    monto_horas_extra_automaticas = _to_decimal(
        horas_extra_automaticas * valor_hora_base * Decimal("2")
    )
    monto_horas_extra_extraordinarias = _to_decimal(
        horas_extra_extraordinarias * valor_hora_base * Decimal("2")
    )

    subtotal_horas = _to_decimal(
        monto_horas_base
        + monto_horas_extra_automaticas
        + monto_horas_extra_extraordinarias
    )
    monto_feriado = _to_decimal(horas_feriado * valor_hora_base)

    # Si se pide asistencia perfecta, usamos el valor actual de la categoría
    # solo como referencia de corrección, sin alterar el valor hora histórico.
    asistencia_perfecta = (
        _to_decimal(liquidacion.empleado.categoria.monto_asistencia_perfecta)
        if aplicar_asistencia_perfecta
        else Decimal("0.00")
    )

    total_descuentos = _to_decimal(
        descuento_cuenta_corriente
        + descuento_adelanto
        + descuento_varios
    )
    total_neto = _to_decimal(
        subtotal_horas + monto_feriado + asistencia_perfecta - total_descuentos
    )

    fecha_actual = datetime.now()
    total_en_letras = _construir_total_en_letras(
        empleado=liquidacion.empleado,
        mes=liquidacion.mes,
        anio=liquidacion.anio,
        total_neto=total_neto,
        fecha_actual=fecha_actual,
    )

    # Actualizamos solo los campos permitidos dentro de la liquidación.
    liquidacion.horas_extra_extraordinarias = horas_extra_extraordinarias
    liquidacion.horas_feriado = horas_feriado
    liquidacion.subtotal_horas = subtotal_horas
    liquidacion.monto_feriado = monto_feriado
    liquidacion.asistencia_perfecta = asistencia_perfecta
    liquidacion.total_descuentos = total_descuentos
    liquidacion.total_neto = total_neto
    liquidacion.total_en_letras = total_en_letras
    liquidacion.fecha_generacion = fecha_actual

    # Borramos el detalle previo y lo regeneramos con los nombres de conceptos
    # actuales para que la corrección quede consistente.
    db.execute(
        delete(LiquidacionDetalle).where(
            LiquidacionDetalle.liquidacion_id == liquidacion.id
        )
    )

    detalles = _construir_detalles_liquidacion(
        monto_horas_base=monto_horas_base,
        monto_horas_extra_automaticas=monto_horas_extra_automaticas,
        monto_horas_extra_extraordinarias=monto_horas_extra_extraordinarias,
        monto_feriado=monto_feriado,
        asistencia_perfecta=asistencia_perfecta,
        descuento_cuenta_corriente=descuento_cuenta_corriente,
        descuento_adelanto=descuento_adelanto,
        descuento_varios=descuento_varios,
    )

    db.flush()

    for detalle in detalles:
        detalle.liquidacion_id = liquidacion.id
        db.add(detalle)

    db.commit()
    db.refresh(liquidacion)

    for detalle in detalles:
        db.refresh(detalle)

    liquidacion.detalles = detalles
    return ResultadoLiquidacion(liquidacion=liquidacion, detalles=detalles)
