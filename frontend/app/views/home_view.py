"""Vista principal del frontend."""

import flet as ft

from app.services.api_client import probar_backend


def build_home_view(page: ft.Page) -> ft.Control:
    """Construye la vista inicial con una prueba basica al backend."""

    # Este texto se actualiza luego de intentar conectar con la API.
    status_text = ft.Text(
        value="Estado: pendiente de prueba",
        size=14,
        color=ft.Colors.BLUE_GREY_700,
    )

    def on_test_connection(_: ft.ControlEvent) -> None:
        """Ejecuta la prueba HTTP y actualiza el estado visible."""

        # Informamos inmediatamente que la app esta intentando conectarse.
        status_text.value = "Estado: probando conexion..."
        status_text.color = ft.Colors.BLUE_GREY_700
        page.update()

        resultado = probar_backend()
        if resultado["ok"]:
            status_text.value = f"Estado: {resultado['message']}"
            status_text.color = ft.Colors.GREEN_700
        else:
            status_text.value = f"Estado: {resultado['message']}"
            status_text.color = ft.Colors.RED_700

        page.update()

    # La vista central se mantiene deliberadamente simple para esta fase:
    # bienvenida, boton de prueba y texto de estado.
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    value="Bienvenido al Sistema de Recibos",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    value=(
                        "Esta pantalla inicial permite verificar si el "
                        "backend esta disponible antes de avanzar."
                    ),
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.ElevatedButton(
                    text="Probar conexion con backend",
                    icon=ft.Icons.CLOUD_DONE_OUTLINED,
                    on_click=on_test_connection,
                ),
                status_text,
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        expand=True,
        padding=30,
    )
