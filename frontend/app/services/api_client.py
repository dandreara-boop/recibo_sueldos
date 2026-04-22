"""Cliente HTTP simple para comunicarse con el backend."""

from __future__ import annotations

import requests

BASE_URL = "http://127.0.0.1:8000"


def probar_backend() -> dict[str, str | bool]:
    """Consulta la raiz del backend y devuelve un resultado amigable."""

    try:
        # Realizamos una llamada simple al endpoint raiz para confirmar que
        # el backend este levantado y respondiendo correctamente.
        response = requests.get(f"{BASE_URL}/", timeout=5)
        response.raise_for_status()

        data = response.json()
        mensaje = data.get("mensaje", "Conexion exitosa con el backend.")
        return {"ok": True, "message": mensaje}
    except requests.RequestException as exc:
        # Si ocurre un problema de red o el backend devuelve error HTTP,
        # devolvemos un mensaje listo para mostrar en pantalla.
        return {"ok": False, "message": f"Error al conectar con el backend: {exc}"}
