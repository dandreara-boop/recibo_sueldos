import flet as ft

from app.views.categorias_view import build_categorias_view
from app.views.configuracion_view import build_configuracion_view
from app.views.empleados_view import build_empleados_view
from app.views.historial_liquidaciones_view import build_historial_liquidaciones_view
from app.views.home_view import build_home_view
from app.views.liquidaciones_view import build_liquidaciones_view


def main(page: ft.Page):
    """Configura la ventana principal y coordina la navegación de vistas."""

    page.title = "Sistema de Recibos"
    page.window_width = 1000
    page.window_height = 700
    page.bgcolor = "#F4F7FB"

    # Este contenedor central se reutiliza para intercambiar vistas sin tocar
    # el navbar actual ni reconstruir toda la pantalla cada vez.
    contenido = ft.Container(expand=True)

    def ir_home(e=None):
        """Muestra el dashboard principal con accesos rápidos."""

        contenido.content = build_home_view(
            page=page,
            on_nueva_liquidacion=ir_liquidaciones,
            on_historial=ir_historial,
            on_reporte_mensual=ir_historial,
            on_configuracion=ir_configuracion,
        )
        page.update()

    def ir_categorias(e=None):
        """Muestra la vista actual de categorías."""

        contenido.content = build_categorias_view(page)
        page.update()

    def ir_empleados(e=None):
        """Muestra la vista actual de empleados."""

        contenido.content = build_empleados_view(page)
        page.update()

    def ir_liquidaciones(e=None):
        """Muestra la vista actual de generación de liquidaciones."""

        contenido.content = build_liquidaciones_view(page)
        page.update()

    def ir_historial(e=None):
        """Muestra la vista actual del historial de liquidaciones."""

        contenido.content = build_historial_liquidaciones_view(page)
        page.update()

    def ir_configuracion(e=None):
        """Muestra una vista simple con accesos a configuración interna."""

        contenido.content = build_configuracion_view(
            page=page,
            on_categorias=ir_categorias,
            on_empleados=ir_empleados,
        )
        page.update()

    # Mantenemos el navbar actual para no romper la navegación existente.
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
                        ft.TextButton("Historial", on_click=ir_historial),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.Colors.BLUE_700,
        padding=15,
    )

    page.add(
        ft.Column(
            controls=[
                navbar,
                contenido,
            ],
            expand=True,
        )
    )

    ir_home()


ft.app(target=main)
