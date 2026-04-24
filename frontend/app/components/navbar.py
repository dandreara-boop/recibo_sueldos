"""Barra superior simple para la ventana principal."""

import flet as ft


def build_navbar() -> ft.Control:
    """Devuelve una barra superior minimalista para la aplicacion."""

    # Mantenemos un encabezado simple y claro mientras el frontend todavia
    # esta en su fase inicial.
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    value="Sistema de Recibos internos",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.BLUE_700,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
    )
