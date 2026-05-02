import webbrowser

import flet as ft

from app.services.api_client import (
    BASE_URL,
    generar_liquidacion,
    listar_empleados,
)


def build_liquidaciones_view(page: ft.Page) -> ft.Control:
    """
    Vista para generar liquidaciones.
    """

    empleado_dropdown = ft.Dropdown(label="Empleado", width=320)

    mes_input = ft.TextField(
        label="Mes (1-12)",
        width=120,
    )

    anio_input = ft.TextField(
        label="Año",
        width=120,
    )

    horas_info_text = ft.Text(
        value=(
            "Las horas laborables del mes serán calculadas automáticamente "
            "por el backend. La liquidación paga 208 hs base como mínimo."
        ),
        size=14,
        color=ft.Colors.BLUE_GREY_700,
    )

    feriado_input = ft.TextField(
        label="Horas feriado",
        width=180,
        value="0",
    )

    horas_extra_extraordinarias_input = ft.TextField(
        label="Horas extra extraordinarias",
        width=220,
        value="0",
    )

    aplicar_asistencia_checkbox = ft.Checkbox(
        label="Aplicar asistencia perfecta",
        value=False,
    )

    cuenta_corriente_input = ft.TextField(
        label="Cuenta corriente",
        width=180,
        value="0",
    )

    adelanto_input = ft.TextField(
        label="Adelanto",
        width=180,
        value="0",
    )

    varios_input = ft.TextField(
        label="Varios",
        width=180,
        value="0",
    )

    resultado_text = ft.Text()

    def cargar_empleados():
        """
        Consulta empleados al backend y llena el dropdown.
        """
        res = listar_empleados()

        if not res["ok"]:
            resultado_text.value = res["message"]
            resultado_text.color = ft.Colors.RED
            page.update()
            return

        empleado_dropdown.options = [
            ft.dropdown.Option(
                key=str(empleado["id"]),
                text=f"{empleado['apellido']}, {empleado['nombre']}",
            )
            for empleado in res["data"]
        ]
        page.update()

    def on_generar(e):
        """
        Toma los datos del formulario y solicita al backend
        la generación de la liquidación.
        """
        if not empleado_dropdown.value:
            resultado_text.value = "Debes seleccionar un empleado."
            resultado_text.color = ft.Colors.RED
            page.update()
            return

        try:
            payload = {
                "empleado_id": int(empleado_dropdown.value),
                "mes": int(mes_input.value),
                "anio": int(anio_input.value),
                "horas_feriado": float(feriado_input.value or 0),
                "horas_extra_extraordinarias": float(
                    horas_extra_extraordinarias_input.value or 0
                ),
                "aplicar_asistencia_perfecta": aplicar_asistencia_checkbox.value,
                "descuento_cuenta_corriente": float(
                    cuenta_corriente_input.value or 0
                ),
                "descuento_adelanto": float(adelanto_input.value or 0),
                "descuento_varios": float(varios_input.value or 0),
            }
        except Exception:
            resultado_text.value = "Error en los datos ingresados."
            resultado_text.color = ft.Colors.RED
            page.update()
            return

        resultado_text.value = "Generando liquidación..."
        resultado_text.color = ft.Colors.BLUE_GREY_700
        page.update()

        res = generar_liquidacion(payload)
       # print("RESPUESTA:", res["data"])
        
        #print("ID GENERADO:", res["data"]["id"])

        if res["ok"]:
            liquidacion_id = res["data"]["id"]
            horas_laborables = res["data"]["horas_laborables_mes"]
            horas_base = res["data"]["horas_base_pagadas"]

            resultado_text.value = (
                f"Liquidación generada correctamente (ID {liquidacion_id}). "
                f"Horas laborables del mes: {horas_laborables}. "
                f"Horas base pagadas: {horas_base}."
            )
            resultado_text.color = ft.Colors.GREEN
            page.update()

            pdf_url = f"{BASE_URL}/liquidaciones/{liquidacion_id}/pdf"
            page.launch_url(pdf_url)
        else:
            resultado_text.value = res["message"]
            resultado_text.color = ft.Colors.RED
            page.update()

    cargar_empleados()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Generar liquidación",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "El sistema calcula las horas laborables del mes y liquida 208 hs base como mínimo.",
                    size=16,
                    color=ft.Colors.BLUE_GREY_700,
                ),
                empleado_dropdown,
                ft.Row(
                    [
                        mes_input,
                        anio_input,
                    ],
                    wrap=True,
                ),
                horas_info_text,
                ft.Row(
                    [
                        feriado_input,
                        horas_extra_extraordinarias_input,
                    ],
                    wrap=True,
                ),
                aplicar_asistencia_checkbox,
                ft.Text(
                    "Descuentos",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        cuenta_corriente_input,
                        adelanto_input,
                        varios_input,
                    ],
                    wrap=True,
                ),
                # Reemplazamos ElevatedButton por Button para alinearnos con
                # el componente recomendado por Flet sin alterar la lógica.
                ft.Button(
                    content="Generar liquidación",
                    icon=ft.Icons.RECEIPT_LONG,
                    on_click=on_generar,
                ),
                resultado_text,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )
