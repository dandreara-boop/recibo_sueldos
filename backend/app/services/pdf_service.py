"""Servicios para generar PDFs de liquidaciones."""

from __future__ import annotations

from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.empleado import Empleado
from app.models.liquidacion import Liquidacion


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


def obtener_liquidacion_para_pdf(
    db: Session,
    liquidacion_id: int,
) -> Liquidacion | None:
    """
    Busca una liquidación con todos los datos necesarios para exportarla.

    Trae:
    - empleado
    - detalles
    """

    stmt = (
        select(Liquidacion)
        .options(
            joinedload(Liquidacion.empleado).joinedload(Empleado.categoria),
            selectinload(Liquidacion.detalles),
        )
        .where(Liquidacion.id == liquidacion_id)
    )
    return db.scalar(stmt)


def _formatear_importe(valor: Decimal) -> str:
    """
    Devuelve un importe con dos decimales.
    """
    return f"{valor:.2f}"


def _crear_estilos():
    """
    Prepara los estilos base para el PDF.
    """
    estilos = getSampleStyleSheet()

    estilos.add(
        ParagraphStyle(
            name="TituloRecibo",
            parent=estilos["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            alignment=1,
            spaceAfter=8,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="TextoRecibo",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            spaceAfter=2,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="TextoLegal",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            spaceAfter=4,
        )
    )

    estilos.add(
        ParagraphStyle(
            name="Firma",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            alignment=1,
            spaceAfter=2,
        )
    )

    return estilos


def _calcular_total_haberes(liquidacion: Liquidacion) -> Decimal:
    """
    Suma todos los detalles de tipo 'haber'.
    """
    total = Decimal("0")
    for detalle in liquidacion.detalles:
        if detalle.tipo == "haber":
            total += Decimal(detalle.importe)
    return total


def _crear_tabla_detalles(liquidacion: Liquidacion) -> Table:
    """
    Construye la tabla principal del recibo con columnas:
    Concepto | Haberes | Descuentos
    """
    datos_tabla = [["Concepto", "Haberes", "Descuentos"]]

    detalles_ordenados = sorted(liquidacion.detalles, key=lambda item: item.orden)

    for detalle in detalles_ordenados:
        haber = ""
        descuento = ""

        if detalle.tipo == "haber":
            haber = f"$ {_formatear_importe(Decimal(detalle.importe))}"
        elif detalle.tipo == "descuento":
            descuento = f"$ {_formatear_importe(Decimal(detalle.importe))}"

        datos_tabla.append(
            [
                detalle.concepto,
                haber,
                descuento,
            ]
        )

    total_haberes = _calcular_total_haberes(liquidacion)

    datos_tabla.append(
        [
            "Totales",
            f"$ {_formatear_importe(total_haberes)}",
            f"$ {_formatear_importe(Decimal(liquidacion.total_descuentos))}",
        ]
    )

    datos_tabla.append(
        [
            "Neto a cobrar",
            "",
            f"$ {_formatear_importe(Decimal(liquidacion.total_neto))}",
        ]
    )

    tabla = Table(
        datos_tabla,
        colWidths=[5.8 * cm, 3.0 * cm, 3.0 * cm],
        repeatRows=1,
    )

    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e2f3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -3), [colors.white, colors.HexColor("#f7f7f7")]),
                ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#eeeeee")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dddddd")),
                ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 1), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )

    return tabla


def _crear_bloque_recibo(
    liquidacion: Liquidacion,
    estilos,
    texto_firma: str,
) -> Table:
    """
    Construye una copia del recibo.

    Se devuelve como una tabla contenedora para poder poner
    dos copias lado a lado en la misma hoja.
    """
    empleado = liquidacion.empleado
    periodo = f"{MESES.get(liquidacion.mes, str(liquidacion.mes)).capitalize()} de {liquidacion.anio}"

    elementos = []

    # Título
    elementos.append(Paragraph("RECIBO INTERNO", estilos["TituloRecibo"]))

    # Datos del empleado
    elementos.append(
        Paragraph(
            f"<b>Empleado:</b> {empleado.nombre} {empleado.apellido}",
            estilos["TextoRecibo"],
        )
    )
    # elementos.append(
    #     Paragraph(f"<b>DNI:</b> {empleado.dni}", estilos["TextoRecibo"])
    # )
    # elementos.append(
    #     Paragraph(
    #         f"<b>Domicilio:</b> {empleado.domicilio}",
    #         estilos["TextoRecibo"],
    #     )
    # )
    elementos.append(
        Paragraph(
            f"<b>Periodo:</b> {periodo}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(Spacer(1, 0.20 * cm))

    # Tabla de conceptos
    elementos.append(_crear_tabla_detalles(liquidacion))
    elementos.append(Spacer(1, 0.25 * cm))

    # Texto legal
    elementos.append(
        Paragraph("<b>Texto legal:</b>", estilos["TextoRecibo"])
    )
    elementos.append(
        Paragraph(liquidacion.total_en_letras, estilos["TextoLegal"])
    )

    elementos.append(Spacer(1, 0.70 * cm))

    # Firma
    elementos.append(
        Paragraph("______________________________", estilos["Firma"])
    )
    elementos.append(
        Paragraph(texto_firma, estilos["Firma"])
    )

    # Armamos una tabla contenedora de una sola celda.
    # Esto ayuda a que ReportLab la ubique mejor lado a lado.
    contenedor = Table(
        [[elementos]],
        colWidths=[12.2 * cm],
    )

    contenedor.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return contenedor


def generar_pdf_liquidacion(liquidacion: Liquidacion) -> bytes:
    """
    Genera un PDF en memoria para una liquidación existente.

    El PDF sale en horizontal y contiene dos copias:
    - copia para firma del empleado
    - copia para firma del empleador
    """
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    estilos = _crear_estilos()
    elementos = []

    copia_empleado = _crear_bloque_recibo(
        liquidacion=liquidacion,
        estilos=estilos,
        texto_firma="Firma del empleado",
    )

    copia_empleador = _crear_bloque_recibo(
        liquidacion=liquidacion,
        estilos=estilos,
        texto_firma="Firma del empleador",
    )

    # Tabla principal con las dos copias lado a lado
    tabla_principal = Table(
        [[copia_empleado, copia_empleador]],
        colWidths=[13.0 * cm, 13.0 * cm],
    )

    tabla_principal.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elementos.append(tabla_principal)

    documento.build(elementos)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes