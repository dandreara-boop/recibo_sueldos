import flet as ft

from app.services.api_client import (
    actualizar_categoria,
    crear_categoria,
    listar_categorias,
)


def build_categorias_view(page: ft.Page) -> ft.Control:
    """
    Vista para listar, crear y editar categorías.
    """

    categoria_en_edicion_id: dict[str, int | None] = {"value": None}

    nombre_input = ft.TextField(
        label="Nombre de la categoría",
        width=300,
    )

    valor_hora_input = ft.TextField(
        label="Valor hora",
        width=200,
    )
    asistencia_input = ft.TextField(
    label="Asistencia perfecta",
    width=200,
    value="0",
    )
    mensaje_text = ft.Text(
        value="",
        size=14,
    )
    # Usamos el nuevo componente Button recomendado por Flet para evitar
    # warnings de deprecación sin cambiar el comportamiento actual.
    boton_guardar = ft.Button(
        content="Crear categoría",
        icon=ft.Icons.ADD,
    )
    boton_cancelar = ft.OutlinedButton(
        "Cancelar edición",
        icon=ft.Icons.CANCEL_OUTLINED,
        visible=False,
    )

    lista_categorias = ft.Column(spacing=10)

    def limpiar_formulario() -> None:
        """
        Restablece el formulario al modo alta.
        """

        categoria_en_edicion_id["value"] = None
        nombre_input.value = ""
        nombre_input.disabled = False
        valor_hora_input.value = ""
        asistencia_input.value = "0"
        boton_guardar.content = "Crear categoría"
        boton_guardar.icon = ft.Icons.ADD
        boton_cancelar.visible = False

    def iniciar_edicion(categoria: dict) -> None:
        """
        Carga los datos de una categoría en el formulario para editar.
        """

        categoria_en_edicion_id["value"] = categoria["id"]
        nombre_input.value = categoria["nombre"]
        nombre_input.disabled = True
        valor_hora_input.value = str(categoria["valor_hora"])
        asistencia_input.value = str(categoria["monto_asistencia_perfecta"])
        boton_guardar.content = "Guardar cambios"
        boton_guardar.icon = ft.Icons.SAVE_OUTLINED
        boton_cancelar.visible = True
        mensaje_text.value = (
            f"Editando categoría: {categoria['nombre']}"
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
                            color=ft.Colors.BLACK,
                        ),
                        ft.Text(
                            value=f"Nombre: {categoria['nombre']}",
                            width=250,
                            color=ft.Colors.BLACK,
                        ),
                        ft.Text(
                            value=f"Valor hora: ${categoria['valor_hora']}",
                            width=180,
                            color=ft.Colors.BLACK,
                        ),
                        ft.Text(
                            value=f"Asistencia: ${categoria['monto_asistencia_perfecta']}",
                            width=200,
                            color=ft.Colors.BLACK,
                        ),
                        ft.Button(
                            content="Editar",
                            icon=ft.Icons.EDIT_OUTLINED,
                            on_click=lambda e, categoria=categoria: iniciar_edicion(categoria),
                        ),
                    ]
                ),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
            )
            lista_categorias.controls.append(card)

        page.update()

    def on_guardar_categoria(_: ft.ControlEvent) -> None:
        """
        Toma los datos del formulario y crea o actualiza una categoría.
        """
        nombre = nombre_input.value.strip()
        valor_hora_texto = valor_hora_input.value.strip()
        asistencia_texto = asistencia_input.value.strip()

        if not categoria_en_edicion_id["value"] and not nombre:
            mensaje_text.value = "El nombre no puede estar vacío."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        try:
            valor_hora = float(valor_hora_texto)
            monto_asistencia = float(asistencia_texto or 0)
        except ValueError:
            mensaje_text.value = "Valor hora y asistencia deben ser numéricos."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        if valor_hora <= 0:
            mensaje_text.value = "El valor hora debe ser mayor que 0."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        if monto_asistencia < 0:
            mensaje_text.value = "La asistencia perfecta no puede ser negativa."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        if categoria_en_edicion_id["value"] is None:
            resultado = crear_categoria(nombre, valor_hora, monto_asistencia)
            mensaje_ok = "Categoría creada correctamente."
        else:
            resultado = actualizar_categoria(
                categoria_en_edicion_id["value"],
                valor_hora,
                monto_asistencia,
            )
            mensaje_ok = "Categoría actualizada correctamente."

        if resultado["ok"]:
            mensaje_text.value = mensaje_ok
            mensaje_text.color = ft.Colors.GREEN
            limpiar_formulario()
            cargar_categorias()
            page.update()
        else:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()

    boton_guardar.on_click = on_guardar_categoria
    boton_cancelar.on_click = on_cancelar_edicion

    # Cargamos la lista al entrar por primera vez a la vista
    cargar_categorias()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Categorías",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Text(
                    "Alta, edición y listado de categorías",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Row(
                    controls=[
                        nombre_input,
                        valor_hora_input,
                        asistencia_input,
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
                    color=ft.Colors.BLACK,
                ),
                lista_categorias,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
        
    )
