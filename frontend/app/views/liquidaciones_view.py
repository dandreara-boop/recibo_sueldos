import flet as ft
import webbrowser
from app.services.api_client import (
    generar_liquidacion,
    listar_empleados,
)


def build_liquidaciones_view(page: ft.Page) -> ft.Control:
    """
    Vista para generar liquidaciones.
    """

    empleado_dropdown = ft.Dropdown(label="Empleado", width=300)

    mes_input = ft.TextField(label="Mes (1-12)", width=120)
    anio_input = ft.TextField(label="Año", width=120)

    horas_input = ft.TextField(label="Horas trabajadas", width=200)
    feriado_input = ft.TextField(label="Horas feriado", width=200)
    asistencia_input = ft.TextField(label="Asistencia perfecta",width=200)
    cuenta_corriente_input = ft.TextField(label="Cuenta corriente", width=200)
    adelanto_input = ft.TextField(label="Adelanto", width=200)
    varios_input = ft.TextField(label="Varios", width=200)

    resultado_text = ft.Text()

    def cargar_empleados():
        res = listar_empleados()
        if not res["ok"]:
            resultado_text.value = res["message"]
            resultado_text.color = ft.Colors.RED
            page.update()
            return

        empleado_dropdown.options = [
            ft.dropdown.Option(
                key=str(e["id"]),
                text=f"{e['apellido']}, {e['nombre']}",
            )
            for e in res["data"]
        ]
        page.update()

    def on_generar(e):
        try:
            payload = {
            "empleado_id": int(empleado_dropdown.value),
            "mes": int(mes_input.value),
            "anio": int(anio_input.value),
            "horas_totales": float(horas_input.value),
            "horas_feriado": float(feriado_input.value or 0),
            "asistencia_perfecta": 0,
            "descuento_cuenta_corriente": float(cuenta_corriente_input.value or 0),
            "descuento_adelanto": float(adelanto_input.value or 0),
            "descuento_varios": float(varios_input.value or 0),
        }
        except Exception:
            resultado_text.value = "Error en los datos ingresados."
            resultado_text.color = ft.Colors.RED
            page.update()
            return

        res = generar_liquidacion(payload)

        if res["ok"]:
            liquidacion_id = res["data"]["id"]
            resultado_text.value = f"Liquidación generada (ID {liquidacion_id})"
            resultado_text.color = ft.Colors.GREEN

            # abrir PDF automáticamente
            pdf_url = f"http://127.0.0.1:8000/liquidaciones/{liquidacion_id}/pdf"
            webbrowser.open(pdf_url)
        else:
            resultado_text.value = res["message"]
            resultado_text.color = ft.Colors.RED

        page.update()

    cargar_empleados()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Generar liquidación", size=24, weight=ft.FontWeight.BOLD),

                empleado_dropdown,

                ft.Row([mes_input, anio_input]),
                ft.Row([horas_input, feriado_input, asistencia_input]),


                ft.Text("Descuentos", weight=ft.FontWeight.BOLD),
                ft.Row([cuenta_corriente_input, adelanto_input, varios_input]),

                ft.ElevatedButton(
                    "Generar liquidación",
                    icon=ft.Icons.RECEIPT_LONG,
                    on_click=on_generar,
                ),

                resultado_text,
            ],
            spacing=15,
        ),
        padding=20,
        expand=True,
    )