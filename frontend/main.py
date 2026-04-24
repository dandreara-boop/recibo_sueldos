import flet as ft

from app.components.navbar import build_navbar
from app.views.home_view import build_home_view
from app.views.categorias_view import build_categorias_view
from app.views.empleados_view import build_empleados_view
from app.views.liquidaciones_view import build_liquidaciones_view


def main(page: ft.Page):
    page.title = "Sistema de Recibos"
    page.window_width = 1000
    page.window_height = 700

    # contenedor dinámico (acá se cambian las vistas)
    contenido = ft.Container(expand=True)

    # funciones de navegación
    def ir_home(e=None):
        contenido.content = build_home_view(page)
        page.update()

    def ir_categorias(e):
        contenido.content = build_categorias_view(page)
        page.update()

    def ir_empleados(e):
        contenido.content = build_empleados_view(page)
        page.update()

    def ir_liquidaciones(e):
        contenido.content = build_liquidaciones_view(page)
        page.update()

    # navbar con botones
    navbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    "Sistema de Recibos Internos",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Row(
                    controls=[
                        ft.TextButton("Inicio", on_click=ir_home),
                        ft.TextButton("Categorías", on_click=ir_categorias),
                        ft.TextButton("Empleados", on_click=ir_empleados),
                        ft.TextButton("Liquidaciones", on_click=ir_liquidaciones),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.Colors.BLUE_700,
        padding=15,
    )

    # layout principal
    page.add(
        ft.Column(
            controls=[
                navbar,
                contenido,
            ],
            expand=True,
        )
    )

    # pantalla inicial
    ir_home()


ft.app(target=main)