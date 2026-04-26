import webbrowser

import flet as ft

from app.services.api_client import BASE_URL, listar_liquidaciones


def build_historial_liquidaciones_view(page: ft.Page) -> ft.Control:
    """
    Vista simple para consultar el historial de liquidaciones.
    """

    mensaje_text = ft.Text(value="", size=14)
    lista_historial = ft.Column(spacing=10)

    def abrir_pdf(liquidacion_id: int) -> None:
        """
        Abre en el navegador el PDF de la liquidación seleccionada.
        """

        # Usamos el endpoint ya existente del backend para abrir el recibo
        # directamente desde el navegador del usuario.
        webbrowser.open(f"{BASE_URL}/liquidaciones/{liquidacion_id}/pdf")

    def cargar_historial(_: ft.ControlEvent | None = None) -> None:
        """
        Consulta el backend y vuelve a dibujar el historial.
        """

        mensaje_text.value = "Cargando historial de liquidaciones..."
        mensaje_text.color = ft.Colors.BLUE_GREY_700
        lista_historial.controls.clear()
        page.update()

        resultado = listar_liquidaciones()

        if not resultado["ok"]:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        liquidaciones = resultado["data"]

        if not liquidaciones:
            mensaje_text.value = "No hay liquidaciones generadas todavía."
            mensaje_text.color = ft.Colors.BLUE_GREY_700
            page.update()
            return

        mensaje_text.value = f"Se encontraron {len(liquidaciones)} liquidaciones."
        mensaje_text.color = ft.Colors.GREEN_700

        for liquidacion in liquidaciones:
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value=liquidacion["nombre_completo"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    value=(
                                        f"Periodo: {liquidacion['mes']}/"
                                        f"{liquidacion['anio']}"
                                    ),
                                    size=14,
                                ),
                                ft.Text(
                                    value=(
                                        f"Total neto: $ "
                                        f"{float(liquidacion['total_neto']):.2f}"
                                    ),
                                    size=14,
                                ),
                                ft.Text(
                                    value=(
                                        "Fecha: "
                                        f"{liquidacion['fecha_generacion']}"
                                    ),
                                    size=13,
                                    color=ft.Colors.BLUE_GREY_700,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Abrir PDF",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=lambda e, liquidacion_id=liquidacion["id"]: abrir_pdf(liquidacion_id),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
            )
            lista_historial.controls.append(card)

        page.update()

    cargar_historial()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Historial de liquidaciones",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Consulta las liquidaciones generadas y abre sus PDFs.",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Actualizar",
                            icon=ft.Icons.REFRESH,
                            on_click=cargar_historial,
                        ),
                    ]
                ),
                mensaje_text,
                ft.Divider(),
                lista_historial,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
    )
