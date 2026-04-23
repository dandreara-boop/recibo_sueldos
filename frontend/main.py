import flet as ft

from app.components.navbar import build_navbar
from app.views.empleados_view import build_empleados_view
from app.views.liquidaciones_view import build_liquidaciones_view


def main(page: ft.Page):
    """
    Punto de entrada principal de la app Flet.
    """

    page.title = "Sistema de Recibos"
    page.window_width = 1100
    page.window_height = 750
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    contenido = ft.Container(expand=True)
    contenido.content = build_empleados_view(page)
    

    contenido.content = build_liquidaciones_view(page)

    page.add(
        ft.Column(
            controls=[
                build_navbar(),
                contenido,
            ],
            expand=True,
            spacing=0,
        )
    )


ft.app(target=main)