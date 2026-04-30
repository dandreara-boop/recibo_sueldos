import webbrowser

import flet as ft

from app.services.api_client import (
    BASE_URL,
    abrir_pdf_periodo,
    corregir_liquidacion,
    listar_empleados,
    listar_liquidaciones,
)


def build_historial_liquidaciones_view(page: ft.Page) -> ft.Control:
    """
    Vista simple para consultar el historial de liquidaciones.
    """

    mensaje_text = ft.Text(value="", size=14)
    lista_historial = ft.Column(spacing=10)
    empleado_dropdown = ft.Dropdown(
        label="Empleado",
        width=280,
        options=[ft.dropdown.Option(key="", text="Todos")],
        value="",
    )
    mes_input = ft.TextField(label="Mes", width=120)
    anio_input = ft.TextField(label="Año", width=140)
    dialogo_correccion = ft.AlertDialog(modal=True)

    def abrir_pdf(liquidacion_id: int) -> None:
        """
        Abre en el navegador el PDF de la liquidación seleccionada.
        """

        # Usamos el endpoint ya existente del backend para abrir el recibo
        # directamente desde el navegador del usuario.
        webbrowser.open(f"{BASE_URL}/liquidaciones/{liquidacion_id}/pdf")

    def abrir_modal_correccion(liquidacion: dict) -> None:
        """
        Abre un modal sencillo para corregir una liquidación existente.
        """

        # El historial resumido ahora incluye las horas de feriado y el
        # desglose de descuentos, por lo que podemos abrir el modal con todos
        # los valores actuales ya precargados para facilitar la corrección.
        horas_extra_input = ft.TextField(
            label="Horas extra extraordinarias",
            value=str(liquidacion.get("horas_extra_extraordinarias", 0)),
            width=240,
        )
        horas_feriado_input = ft.TextField(
            label="Horas feriado",
            value=str(liquidacion.get("horas_feriado", 0)),
            width=240,
        )
        descuento_cc_input = ft.TextField(
            label="Descuento cuenta corriente",
            value=str(liquidacion.get("descuento_cuenta_corriente", 0)),
            width=240,
        )
        descuento_adelanto_input = ft.TextField(
            label="Descuento adelanto",
            value=str(liquidacion.get("descuento_adelanto", 0)),
            width=240,
        )
        descuento_varios_input = ft.TextField(
            label="Descuento varios",
            value=str(liquidacion.get("descuento_varios", 0)),
            width=240,
        )
        asistencia_checkbox = ft.Checkbox(
            label="Aplicar asistencia perfecta",
            value=float(liquidacion.get("asistencia_perfecta", 0)) > 0,
        )
        mensaje_modal = ft.Text(value="", size=13)

        def cerrar_modal(_: ft.ControlEvent | None = None) -> None:
            """
            Cierra el modal de corrección.
            """

            dialogo_correccion.open = False
            page.update()

        def guardar_correccion(_: ft.ControlEvent) -> None:
            """
            Envía la corrección al backend y refresca el historial.
            """

            try:
                horas_extra = float(horas_extra_input.value or 0)
                horas_feriado = float(horas_feriado_input.value or 0)
                descuento_cc = float(descuento_cc_input.value or 0)
                descuento_adelanto = float(descuento_adelanto_input.value or 0)
                descuento_varios = float(descuento_varios_input.value or 0)
            except ValueError:
                mensaje_modal.value = "Todos los importes y horas deben ser numéricos."
                mensaje_modal.color = ft.Colors.RED
                page.update()
                return

            if (
                horas_extra < 0
                or horas_feriado < 0
                or descuento_cc < 0
                or descuento_adelanto < 0
                or descuento_varios < 0
            ):
                mensaje_modal.value = "Los valores no pueden ser negativos."
                mensaje_modal.color = ft.Colors.RED
                page.update()
                return

            resultado = corregir_liquidacion(
                liquidacion_id=liquidacion["id"],
                horas_extra_extraordinarias=horas_extra,
                horas_feriado=horas_feriado,
                aplicar_asistencia_perfecta=bool(asistencia_checkbox.value),
                descuento_cuenta_corriente=descuento_cc,
                descuento_adelanto=descuento_adelanto,
                descuento_varios=descuento_varios,
            )

            if not resultado["ok"]:
                mensaje_modal.value = resultado["message"]
                mensaje_modal.color = ft.Colors.RED
                page.update()
                return

            cerrar_modal()
            mensaje_text.value = (
                f"Liquidación {liquidacion['id']} corregida correctamente."
            )
            mensaje_text.color = ft.Colors.GREEN_700
            cargar_historial()

        MESES = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }

        nombre_mes = MESES.get(liquidacion["mes"], f"Mes {liquidacion['mes']}")

        dialogo_correccion.title = ft.Text(
            value=(
                f"{liquidacion['nombre_completo']} - "
                f"{nombre_mes} {liquidacion['anio']}"
            )
        )
     
        dialogo_correccion.content = ft.Column(
            controls=[
                ft.Text(
                    value=(
                        "Completá solo los valores que querés recalcular. "
                        "Los importes y horas no pueden ser negativos."
                    ),
                    size=14,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                horas_extra_input,
                horas_feriado_input,
                descuento_cc_input,
                descuento_adelanto_input,
                descuento_varios_input,
                asistencia_checkbox,
                mensaje_modal,
            ],
            tight=True,
            spacing=12,
        )
        dialogo_correccion.actions = [
            ft.TextButton("Cancelar", on_click=cerrar_modal),
            ft.ElevatedButton("Guardar corrección", on_click=guardar_correccion),
        ]
        dialogo_correccion.actions_alignment = ft.MainAxisAlignment.END
        
        if dialogo_correccion not in page.overlay:
            page.overlay.append(dialogo_correccion)

        dialogo_correccion.open = True
        page.update()

    def cargar_empleados() -> None:
        """
        Consulta empleados al backend y llena el filtro desplegable.
        """

        resultado = listar_empleados()
        if not resultado["ok"]:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        empleado_dropdown.options = [ft.dropdown.Option(key="", text="Todos")]
        empleado_dropdown.options.extend(
            [
                ft.dropdown.Option(
                    key=str(empleado["id"]),
                    text=f"{empleado['apellido']}, {empleado['nombre']}",
                )
                for empleado in resultado["data"]
            ]
        )
        page.update()

    def _leer_filtros() -> tuple[int | None, int | None, int | None] | None:
        """
        Lee y valida los filtros ingresados por el usuario.
        """

        empleado_id = int(empleado_dropdown.value) if empleado_dropdown.value else None

        try:
            mes = int(mes_input.value) if mes_input.value.strip() else None
            anio = int(anio_input.value) if anio_input.value.strip() else None
        except ValueError:
            mensaje_text.value = "Mes y año deben ser numéricos."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return None

        if mes is not None and (mes < 1 or mes > 12):
            mensaje_text.value = "El mes debe estar entre 1 y 12."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return None

        if anio is not None and anio <= 0:
            mensaje_text.value = "El año debe ser mayor que 0."
            mensaje_text.color = ft.Colors.RED
            page.update()
            return None

        return empleado_id, mes, anio

    def cargar_historial(_: ft.ControlEvent | None = None) -> None:
        """
        Consulta el backend y vuelve a dibujar el historial.
        """

        filtros = _leer_filtros()
        if filtros is None:
            return

        empleado_id, mes, anio = filtros

        mensaje_text.value = "Cargando historial de liquidaciones..."
        mensaje_text.color = ft.Colors.BLUE_GREY_700
        lista_historial.controls.clear()
        page.update()

        resultado = listar_liquidaciones(
            empleado_id=empleado_id,
            mes=mes,
            anio=anio,
        )

        if not resultado["ok"]:
            mensaje_text.value = resultado["message"]
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        liquidaciones = resultado["data"]

        if not liquidaciones:
            mensaje_text.value = "No hay liquidaciones generadas todavía."
            mensaje_text.color = ft.Colors.BLUE_GREY_700
            page.update()
            return

        mensaje_text.value = f"Se encontraron {len(liquidaciones)} liquidaciones."
        mensaje_text.color = ft.Colors.GREEN_700

        for liquidacion in liquidaciones:
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value=liquidacion["nombre_completo"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    value=(
                                        f"Periodo: {liquidacion['mes']}/"
                                        f"{liquidacion['anio']}"
                                    ),
                                    size=14,
                                ),
                                ft.Text(
                                    value=(
                                        f"Total neto: $ "
                                        f"{float(liquidacion['total_neto']):.2f}"
                                    ),
                                    size=14,
                                ),
                                ft.Text(
                                    value=(
                                        "Fecha: "
                                        f"{liquidacion['fecha_generacion']}"
                                    ),
                                    size=13,
                                    color=ft.Colors.BLUE_GREY_700,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Abrir PDF",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=lambda e, liquidacion_id=liquidacion["id"]: abrir_pdf(liquidacion_id),
                        ),
                        ft.OutlinedButton(
                            "Corregir",
                            icon=ft.Icons.EDIT_NOTE,
                            on_click=lambda e, liquidacion=liquidacion: abrir_modal_correccion(liquidacion),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
            )
            lista_historial.controls.append(card)

        page.update()

    def limpiar_filtros(_: ft.ControlEvent) -> None:
        """
        Limpia los filtros y vuelve a consultar todo el historial.
        """

        empleado_dropdown.value = ""
        mes_input.value = ""
        anio_input.value = ""
        cargar_historial()

    def on_pdf_periodo(_: ft.ControlEvent) -> None:
        """
        Abre el PDF masivo del período filtrado.
        """

        filtros = _leer_filtros()
        if filtros is None:
            return

        empleado_id, mes, anio = filtros

        if mes is None or anio is None:
            mensaje_text.value = (
                "Para generar el PDF del período debes indicar mes y año."
            )
            mensaje_text.color = ft.Colors.RED
            page.update()
            return

        # Abrimos la URL generada por el cliente API para mantener toda la
        # lógica de armado de endpoints centralizada.
        webbrowser.open(
            abrir_pdf_periodo(
                mes=mes,
                anio=anio,
                empleado_id=empleado_id,
            )
        )

    cargar_empleados()
    cargar_historial()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Historial de liquidaciones",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Consulta las liquidaciones generadas y abre sus PDFs.",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                ft.Row(
                    controls=[
                        empleado_dropdown,
                        mes_input,
                        anio_input,
                    ],
                    wrap=True,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Buscar",
                            icon=ft.Icons.SEARCH,
                            on_click=cargar_historial,
                        ),
                        ft.OutlinedButton(
                            "Limpiar filtros",
                            icon=ft.Icons.CLEAR,
                            on_click=limpiar_filtros,
                        ),
                        ft.ElevatedButton(
                            "Actualizar",
                            icon=ft.Icons.REFRESH,
                            on_click=cargar_historial,
                        ),
                        ft.ElevatedButton(
                            "PDF del período",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=on_pdf_periodo,
                        ),
                    ]
                ),
                mensaje_text,
                ft.Divider(),
                lista_historial,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=20,
    )
