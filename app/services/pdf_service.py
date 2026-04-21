"""Servicios para generar PDFs de liquidaciones."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
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


def obtener_liquidacion_para_pdf(db: Session, liquidacion_id: int) -> Liquidacion | None:
    """Busca una liquidacion con todos los datos necesarios para exportarla."""

    # Traemos empleado, categoria y detalles en la misma operacion para que la
    # generacion del PDF no dependa de cargas perezosas posteriores.
    stmt = (
        select(Liquidacion)
        .options(
            joinedload(Liquidacion.empleado).joinedload(Empleado.categoria),
            selectinload(Liquidacion.detalles),
        )
        .where(Liquidacion.id == liquidacion_id)
    )
    return db.scalar(stmt)


def _formatear_importe(valor) -> str:
    """Devuelve un importe con dos decimales para el recibo."""

    return f"{valor:.2f}"


def _crear_estilos():
    """Prepara estilos base para el PDF."""

    estilos = getSampleStyleSheet()
    estilos.add(
        ParagraphStyle(
            name="TituloRecibo",
            parent=estilos["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=1,
            spaceAfter=12,
        )
    )
    estilos.add(
        ParagraphStyle(
            name="TextoRecibo",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )
    )
    estilos.add(
        ParagraphStyle(
            name="TextoLegal",
            parent=estilos["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            spaceBefore=8,
        )
    )
    return estilos


def generar_pdf_liquidacion(liquidacion: Liquidacion) -> bytes:
    """Genera un PDF en memoria para una liquidacion ya existente."""

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    estilos = _crear_estilos()
    empleado = liquidacion.empleado
    categoria = empleado.categoria
    elementos = []

    # Agregamos una cabecera simple pero clara para identificar el documento.
    elementos.append(Paragraph("RECIBO DE SUELDO", estilos["TituloRecibo"]))
    elementos.append(
        Paragraph(
            f"<b>Empleado:</b> {empleado.nombre} {empleado.apellido}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(
        Paragraph(f"<b>DNI:</b> {empleado.dni}", estilos["TextoRecibo"])
    )
    elementos.append(
        Paragraph(
            f"<b>Domicilio:</b> {empleado.domicilio}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(
        Paragraph(
            f"<b>Categoria:</b> {categoria.nombre}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(
        Paragraph(
            f"<b>Periodo:</b> {MESES.get(liquidacion.mes, liquidacion.mes)} "
            f"{liquidacion.anio}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(Spacer(1, 0.4 * cm))

    # Construimos la tabla principal con los conceptos guardados en la
    # liquidacion y sus importes expresados con dos decimales.
    datos_tabla = [["Concepto", "Tipo", "Importe"]]
    for detalle in sorted(liquidacion.detalles, key=lambda item: item.orden):
        datos_tabla.append(
            [
                detalle.concepto,
                detalle.tipo.capitalize(),
                f"$ {_formatear_importe(detalle.importe)}",
            ]
        )

    tabla = Table(
        datos_tabla,
        colWidths=[8.5 * cm, 3.0 * cm, 4.0 * cm],
        repeatRows=1,
    )
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e2f3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )
    elementos.append(tabla)
    elementos.append(Spacer(1, 0.5 * cm))

    # Mostramos el total neto destacado al final del detalle para facilitar su
    # lectura dentro del recibo.
    elementos.append(
        Paragraph(
            f"<b>Total neto:</b> $ {_formatear_importe(liquidacion.total_neto)}",
            estilos["TextoRecibo"],
        )
    )
    elementos.append(
        Paragraph(liquidacion.total_en_letras, estilos["TextoLegal"])
    )


    elementos.append(Spacer(1, 2 * cm))
    elementos.append(Paragraph("__________________________", estilos["TextoRecibo"]))
    elementos.append(Paragraph("Firma del empleado", estilos["TextoRecibo"]))
    
    documento.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
