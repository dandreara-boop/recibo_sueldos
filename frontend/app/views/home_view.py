"""Vista principal tipo dashboard para el frontend."""

import flet as ft




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
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color="#173B67",
                        ),

                    ],
                    spacing=5,
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
