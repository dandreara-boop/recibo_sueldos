"""Vista de configuración con accesos rápidos a catálogos internos."""

import flet as ft
from app.services.api_client import probar_backend





def _build_config_card(
    *,
    titulo: str,
    descripcion: str,
    icono: str,
    color: str,
    on_click,
) -> ft.Control:
    """Crea una card visual para cada opción de configuración."""

    return ft.Container(
        col={"xs": 12, "md": 6},
        bgcolor="#FFFFFF",
        border_radius=24,
        padding=24,
        height=190,
        ink=True,
        on_click=on_click,
        border=ft.border.all(1, "#E6ECF5"),
        content=ft.Column(
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icono, size=28, color=color),
                ),
                ft.Text(
                    titulo,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="#183153",
                ),
                ft.Text(
                    descripcion,
                    size=14,
                    color="#5A6E88",
                ),
                ft.Text(
                    "Abrir",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=color,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=14,
        ),
    )


def build_configuracion_view(page: ft.Page, on_categorias, on_empleados) -> ft.Control:
    """Construye la vista de configuración con accesos a catálogos base."""
    resultado = probar_backend()
    if resultado["ok"]:
        status = ft.Text(
            "🟢 Backend conectado correctamente",
            color=ft.Colors.GREEN_700,
            size=15,
            weight=ft.FontWeight.BOLD,
        )
    else:
        status = ft.Text(
            f"🔴 {resultado['message']}",
            color=ft.Colors.RED_700,
            size=15,
            weight=ft.FontWeight.BOLD,
        )

    # Esta vista actúa como un pequeño hub interno para agrupar pantallas
    # administrativas sin alterar las vistas que ya existen por separado.
    return ft.Container(
        expand=True,
        padding=28,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Configuración",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color="#183153",
                ),
                ft.Text(
                    (
                        "Elegí qué catálogo querés administrar. Desde acá "
                        "podés entrar rápido a categorías y empleados."
                    ),
                    size=16,
                    color="#5A6E88",
                ),
                status,
                ft.ResponsiveRow(
                    controls=[
                        _build_config_card(
                            titulo="Categorías",
                            descripcion=(
                                "Administrá valores hora y asistencia perfecta."
                            ),
                            icono=ft.Icons.CATEGORY_ROUNDED,
                            color="#1769E0",
                            on_click=on_categorias,
                        ),
                        _build_config_card(
                            titulo="Empleados",
                            descripcion=(
                                "Consultá, creá y actualizá datos del personal."
                            ),
                            icono=ft.Icons.GROUP_ROUNDED,
                            color="#0F9D7A",
                            on_click=on_empleados,
                        ),
                        
                    ],
                    columns=12,
                    spacing=20,
                    run_spacing=20,
                ),
            ],
            spacing=24,
            scroll=ft.ScrollMode.AUTO,
        
        ),
    )
