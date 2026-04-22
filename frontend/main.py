"""Punto de entrada de la aplicacion de escritorio en Flet."""

import flet as ft

from app.components.navbar import build_navbar
from app.views.home_view import build_home_view


def main(page: ft.Page) -> None:
    """Configura la ventana principal y monta la vista inicial."""

    # Definimos una ventana simple para esta primera fase del frontend.
    page.title = "Sistema de Recibos"
    page.window_width = 900
    page.window_height = 600
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    # Construimos la pantalla con una barra superior y una vista central
    # sencilla para probar la conexion con el backend.
    page.add(
        ft.Column(
            controls=[
                build_navbar(),
                build_home_view(page),
            ],
            spacing=0,
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
