import flet as ft

from app.services.api_client import (
    actualizar_empleado,
    crear_empleado,
    listar_categorias,
    listar_empleados,
)


def build_empleados_view(page: ft.Page) -> ft.Control:
    """
    Vista para listar, crear y editar empleados.
    """

    empleado_en_edicion_id: dict[str, int | None] = {"value": None}

    nombre_input = ft.TextField(label="Nombre", width=180)
    apellido_input = ft.TextField(label="Apellido", width=180)
    dni_input = ft.TextField(label="DNI", width=150)
    domicilio_input = ft.TextField(label="Domicilio", width=250)

    categoria_dropdown = ft.Dropdown(
        label="Categoría",
        width=220,
        options=[],
    )
    activo_checkbox = ft.Checkbox(
        label="Empleado activo",
        value=True,
    )

    mensaje_text = ft.Text(value="", size=14)
    lista_empleados = ft.Column(spacing=10)
    # Migramos al componente Button recomendado por Flet manteniendo la
    # misma intención visual y la lógica actual de la vista.
    boton_guardar = ft.Button(
        content="Crear empleado",
        icon=ft.Icons.PERSON_ADD,
    )
    boton_cancelar = ft.OutlinedButton(
        "Cancelar edición",
        icon=ft.Icons.CANCEL_OUTLINED,
        visible=False,
    )

    def limpiar_formulario() -> None:
        """
        Restablece el formulario al modo alta.
        """

        empleado_en_edicion_id["value"] = None
        nombre_input.value = ""
        apellido_input.value = ""
        dni_input.value = ""
        domicilio_input.value = ""
        categoria_dropdown.value = None
        activo_checkbox.value = True
        boton_guardar.content = "Crear empleado"
        boton_guardar.icon = ft.Icons.PERSON_ADD
        boton_cancelar.visible = False

    def iniciar_edicion(empleado: dict) -> None:
        """
        Carga los datos del empleado seleccionado en el formulario.
        """

        empleado_en_edicion_id["value"] = empleado["id"]
        nombre_input.value = empleado["nombre"]
        apellido_input.value = empleado["apellido"]
        dni_input.value = empleado["dni"]
        domicilio_input.value = empleado["domicilio"]
        categoria_dropdown.value = str(empleado["categoria_id"])
        activo_checkbox.value = empleado["activo"]
        boton_guardar.content = "Guardar cambios"
        boton_guardar.icon = ft.Icons.SAVE_OUTLINED
        boton_cancelar.visible = True
        mensaje_text.value = (
            f"Editando empleado: {empleado['apellido']}, {empleado['nombre']}"
        )
        mensaje_text.color = ft.Colors.BLUE_700
        page.update()

    def on_cancelar_edicion(_: ft.ControlEvent) -> None:
        """
        Sale del modo edición y limpia el formulario.
        """

        limpiar_formulario()
        mensaje_text.value = "Edición cancelada."
        mensaje_text.color = ft.Colors.BLUE_GREY_700
        page.update()

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
                        ft.Text(
                            f"Activo: {'Sí' if empleado['activo'] else 'No'}"
                        ),
                        ft.Button(
                            content="Editar",
                            icon=ft.Icons.EDIT_OUTLINED,
                            on_click=lambda e, empleado=empleado: iniciar_edicion(empleado),
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

    def on_guardar_empleado(_: ft.ControlEvent) -> None:
        """
        Toma los datos del formulario y crea o actualiza un empleado.
        """
        nombre = nombre_input.value.strip()
        apellido = apellido_input.value.strip()
        dni = dni_input.value.strip()
        domicilio = domicilio_input.value.strip()
        categoria_id = categoria_dropdown.value
        activo = activo_checkbox.value

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

        if empleado_en_edicion_id["value"] is None:
            resultado = crear_empleado(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                domicilio=domicilio,
                categoria_id=int(categoria_id),
            )
            mensaje_ok = "Empleado creado correctamente."
        else:
            resultado = actualizar_empleado(
                empleado_id=empleado_en_edicion_id["value"],
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                domicilio=domicilio,
                categoria_id=int(categoria_id),
                activo=bool(activo),
            )
            mensaje_ok = "Empleado actualizado correctamente."

        if resultado["ok"]:
            mensaje_text.value = mensaje_ok
            mensaje_text.color = ft.Colors.GREEN
            limpiar_formulario()
            cargar_empleados()
            page.update()
        else:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()

    boton_guardar.on_click = on_guardar_empleado
    boton_cancelar.on_click = on_cancelar_edicion

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
                    "Alta, edición y listado de empleados",
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
                        activo_checkbox,
                    ],
                    wrap=True,
                ),
                ft.Row(
                    controls=[
                        boton_guardar,
                        boton_cancelar,
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
