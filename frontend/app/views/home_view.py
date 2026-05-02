"""Vista principal tipo dashboard para el frontend."""

import flet as ft

from app.services.api_client import probar_backend


def _build_dashboard_card(
    *,
    titulo: str,
    descripcion: str,
    icono: str,
    color_fondo: str,
    color_icono: str,
    on_click,
) -> ft.Control:
    """Crea una card grande reutilizable para el dashboard."""

    # La card se construye como un contenedor clickeable con bordes suaves y
    # buena separación interna para que la pantalla se sienta moderna y clara.
    return ft.Container(
        col={"xs": 12, "md": 6},
        ink=True,
        on_click=on_click,
        bgcolor=color_fondo,
        border_radius=24,
        padding=24,
        height=200,
        animate_scale=200,
        content=ft.Column(
            controls=[
                ft.Container(
                    width=56,
                    height=56,
                    border_radius=16,
                    bgcolor=ft.Colors.with_opacity(0.15, color_icono),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icono, size=30, color=color_icono),
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
                    color="#4F637D",
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Abrir",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=color_icono,
                        ),
                        ft.Icon(
                            ft.Icons.ARROW_FORWARD_ROUNDED,
                            size=16,
                            color=color_icono,
                        ),
                    ],
                    spacing=6,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=16,
        ),
    )


def build_home_view(
    page: ft.Page,
    on_nueva_liquidacion,
    on_historial,
    on_reporte_mensual,
    on_configuracion,
) -> ft.Control:
    """Construye el Home con formato de dashboard y accesos principales."""

    status_text = ft.Text(
        value="Estado del backend: pendiente de verificación",
        size=14,
        color="#5C6F87",
    )

    def on_test_connection(_: ft.ControlEvent) -> None:
        """Ejecuta la prueba HTTP y actualiza el estado visible."""

        status_text.value = "Estado del backend: verificando conexión..."
        status_text.color = "#5C6F87"
        page.update()

        resultado = probar_backend()
        if resultado["ok"]:
            status_text.value = f"Estado del backend: {resultado['message']}"
            status_text.color = ft.Colors.GREEN_700
        else:
            status_text.value = f"Estado del backend: {resultado['message']}"
            status_text.color = ft.Colors.RED_700

        page.update()

    # El encabezado combina bienvenida, breve contexto y una acción rápida
    # para revisar la conexión sin quitar protagonismo a las cards principales.
    encabezado = ft.Container(
        bgcolor="#EAF2FF",
        border_radius=28,
        padding=28,
        content=ft.ResponsiveRow(
            controls=[
                ft.Column(
                    col={"xs": 12, "md": 8},
                    controls=[
                        ft.Text(
                            "Panel principal",
                            size=34,
                            weight=ft.FontWeight.BOLD,
                            color="#173B67",
                        ),
                        # ft.Text(
                        #     (
                        #         "Accedé rápido a las tareas más importantes del "
                        #         "sistema: liquidaciones, historial, reportes y "
                        #         "configuración interna."
                        #     ),
                        #     size=16,
                        #     color="#4D6280",
                        # ),
                    ],
                    spacing=5,
                ),
                ft.Column(
                    col={"xs": 12, "md": 4},
                    controls=[
                        # Mantenemos el estilo del botón principal usando el
                        # nuevo componente Button recomendado por Flet.
                        ft.Button(
                            content="Probar conexión con backend",
                            icon=ft.Icons.CLOUD_DONE_OUTLINED,
                            on_click=on_test_connection,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=14),
                                padding=18,
                                bgcolor="#1D5FD0",
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        status_text,
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
            ]
        ),
    )

    # El tablero principal se presenta en una grilla 2x2 sobre escritorio y
    # se adapta en una columna simple cuando el ancho es menor.
    cards = ft.ResponsiveRow(
        controls=[
            _build_dashboard_card(
                titulo="Nueva liquidación",
                descripcion="Generá un nuevo recibo y calculá conceptos salariales.",
                icono=ft.Icons.RECEIPT_LONG_ROUNDED,
                color_fondo="#FFFFFF",
                color_icono="#1769E0",
                on_click=on_nueva_liquidacion,
            ),
            _build_dashboard_card(
                titulo="Historial",
                descripcion="Consultá liquidaciones previas, abrí PDFs y corregí datos.",
                icono=ft.Icons.HISTORY_ROUNDED,
                color_fondo="#FFFFFF",
                color_icono="#0F9D7A",
                on_click=on_historial,
            ),
            _build_dashboard_card(
                titulo="Reporte mensual",
                descripcion="Revisá el período liquidado y accedé al PDF consolidado.",
                icono=ft.Icons.INSIGHTS_ROUNDED,
                color_fondo="#FFFFFF",
                color_icono="#D97706",
                on_click=on_reporte_mensual,
            ),
            _build_dashboard_card(
                titulo="Configuración",
                descripcion="Administrá categorías y empleados desde un solo lugar.",
                icono=ft.Icons.SETTINGS_ROUNDED,
                color_fondo="#FFFFFF",
                color_icono="#7C3AED",
                on_click=on_configuracion,
            ),
        ],
        columns=12,
        spacing=20,
        run_spacing=20,
    )

    return ft.Container(
        expand=True,
        padding=28,
        content=ft.Column(
            controls=[
                encabezado,
                cards,
            ],
            spacing=24,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
