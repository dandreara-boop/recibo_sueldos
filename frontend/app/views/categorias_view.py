import flet as ft

from app.services.api_client import crear_categoria, listar_categorias


def build_categorias_view(page: ft.Page) -> ft.Control:
    """
    Vista para listar y crear categorías.
    """

    nombre_input = ft.TextField(
        label="Nombre de la categoría --esta",
        width=300,
    )

    valor_hora_input = ft.TextField(
        label="Valor hora",
        width=200,
    )

    mensaje_text = ft.Text(
        value="",
        size=14,
    )

    lista_categorias = ft.Column(spacing=10)

    def cargar_categorias():
        """
        Consulta el backend y vuelve a dibujar la lista de categorías.
        """
        lista_categorias.controls.clear()

        resultado = listar_categorias()

        if not resultado["ok"]:
            lista_categorias.controls.append(
                ft.Text(
                    value=resultado["message"],
                    color=ft.Colors.RED,
                )
            )
            page.update()
            return

        categorias = resultado["data"]

        if not categorias:
            lista_categorias.controls.append(
                ft.Text("No hay categorías cargadas todavía.")
            )
            page.update()
            return

        for categoria in categorias:
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            value=f"ID: {categoria['id']}",
                            width=80,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            value=f"Nombre: {categoria['nombre']}",
                            width=250,
                        ),
                        ft.Text(
                            value=f"Valor hora: ${categoria['valor_hora']}",
                            width=180,
                        ),
                    ]
                ),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
            )
            lista_categorias.controls.append(card)

        page.update()

    def on_crear_categoria(e):
        """
        Toma los datos del formulario y crea una categoría.
        """
        nombre = nombre_input.value.strip()
        valor_hora_texto = valor_hora_input.value.strip()

        if not nombre:
            mensaje_text.value = "El nombre no puede estar vacío."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        try:
            valor_hora = float(valor_hora_texto)
        except ValueError:
            mensaje_text.value = "El valor hora debe ser numérico."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        if valor_hora <= 0:
            mensaje_text.value = "El valor hora debe ser mayor que 0."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        resultado = crear_categoria(nombre, valor_hora)

        if resultado["ok"]:
            mensaje_text.value = "Categoría creada correctamente."
            mensaje_text.color = ft.Colors.GREEN
            nombre_input.value = ""
            valor_hora_input.value = ""
            cargar_categorias()
        else:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()

    # Cargamos la lista al entrar por primera vez a la vista
    cargar_categorias()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Categorías",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Alta y listado de categorías",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Row(
                    controls=[
                        nombre_input,
                        valor_hora_input,
                        ft.ElevatedButton(
                            "Crear categoría",
                            icon=ft.Icons.ADD,
                            on_click=on_crear_categoria,
                        ),
                    ],
                    wrap=True,
                ),
                mensaje_text,
                ft.Divider(),
                ft.Text(
                    "Listado actual",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                lista_categorias,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
    )