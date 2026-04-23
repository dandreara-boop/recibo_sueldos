import flet as ft

from app.services.api_client import (
    crear_empleado,
    listar_categorias,
    listar_empleados,
)


def build_empleados_view(page: ft.Page) -> ft.Control:
    """
    Vista para listar y crear empleados.
    """

    nombre_input = ft.TextField(label="Nombre", width=180)
    apellido_input = ft.TextField(label="Apellido", width=180)
    dni_input = ft.TextField(label="DNI", width=150)
    domicilio_input = ft.TextField(label="Domicilio", width=250)

    categoria_dropdown = ft.Dropdown(
        label="Categoría",
        width=220,
        options=[],
    )

    mensaje_text = ft.Text(value="", size=14)
    lista_empleados = ft.Column(spacing=10)

    def cargar_categorias_dropdown():
        """
        Consulta categorías al backend y llena el dropdown.
        """
        resultado = listar_categorias()

        if not resultado["ok"]:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        categorias = resultado["data"]

        categoria_dropdown.options = [
            ft.dropdown.Option(
                key=str(categoria["id"]),
                text=f"{categoria['nombre']} (${categoria['valor_hora']})",
            )
            for categoria in categorias
        ]

        page.update()

    def cargar_empleados():
        """
        Consulta empleados al backend y redibuja la lista.
        """
        lista_empleados.controls.clear()

        resultado = listar_empleados()

        if not resultado["ok"]:
            lista_empleados.controls.append(
                ft.Text(resultado["message"], color=ft.Colors.RED)
            )
            page.update()
            return

        empleados = resultado["data"]

        if not empleados:
            lista_empleados.controls.append(
                ft.Text("No hay empleados cargados todavía.")
            )
            page.update()
            return

        for empleado in empleados:
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{empleado['apellido']}, {empleado['nombre']}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(f"DNI: {empleado['dni']}"),
                        ft.Text(f"Domicilio: {empleado['domicilio']}"),
                        ft.Text(
                            f"Categoría: {empleado['categoria']['nombre']}"
                        ),
                    ],
                    spacing=4,
                ),
                padding=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
            )
            lista_empleados.controls.append(card)

        page.update()

    def on_crear_empleado(e):
        """
        Toma los datos del formulario y crea un empleado.
        """
        nombre = nombre_input.value.strip()
        apellido = apellido_input.value.strip()
        dni = dni_input.value.strip()
        domicilio = domicilio_input.value.strip()
        categoria_id = categoria_dropdown.value

        if not nombre or not apellido or not dni or not domicilio:
            mensaje_text.value = "Todos los campos son obligatorios."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        if not categoria_id:
            mensaje_text.value = "Debes seleccionar una categoría."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        resultado = crear_empleado(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            domicilio=domicilio,
            categoria_id=int(categoria_id),
        )

        if resultado["ok"]:
            mensaje_text.value = "Empleado creado correctamente."
            mensaje_text.color = ft.Colors.GREEN

            nombre_input.value = ""
            apellido_input.value = ""
            dni_input.value = ""
            domicilio_input.value = ""
            categoria_dropdown.value = None

            cargar_empleados()
        else:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()

    # Carga inicial
    cargar_categorias_dropdown()
    cargar_empleados()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Empleados",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Alta y listado de empleados",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Row(
                    controls=[
                        nombre_input,
                        apellido_input,
                        dni_input,
                    ],
                    wrap=True,
                ),
                ft.Row(
                    controls=[
                        domicilio_input,
                        categoria_dropdown,
                        ft.ElevatedButton(
                            "Crear empleado",
                            icon=ft.Icons.PERSON_ADD,
                            on_click=on_crear_empleado,
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
                lista_empleados,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
    )