import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from urllib.parse import urlencode


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def obtener_mensaje_error(response) -> str:
    """
    Intenta leer el mensaje claro enviado por el backend.
    """
    try:
        data = response.json()
        return data.get("detail", "Ocurrió un error.")
    except Exception:
        return "Ocurrió un error inesperado."
    


def probar_backend() -> dict:
    """
    Intenta conectarse al backend y devuelve un resultado simple.
    """
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "message": data.get("mensaje", "Backend respondió correctamente."),
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al conectar con backend: {error}",
        }


def listar_categorias() -> dict:
    """
    Obtiene la lista de categorías desde el backend.
    """
    try:
        response = requests.get(f"{BASE_URL}/categorias/", timeout=5)
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al listar categorías: {error}",
        }


def crear_categoria(
    nombre: str,
    valor_hora: float,
    monto_asistencia_perfecta: float,
) -> dict:
    """
    Envía una nueva categoría al backend.
    """
    try:
        payload = {
            "nombre": nombre,
            "valor_hora": valor_hora,
            "monto_asistencia_perfecta": monto_asistencia_perfecta
        }

        response = requests.post(
            f"{BASE_URL}/categorias/",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al crear categoría: {error}",
        }


def actualizar_categoria(
    categoria_id: int,
    valor_hora: float,
    monto_asistencia_perfecta: float,
) -> dict:
    """
    Envía cambios de una categoría existente al backend.
    """
    try:
        payload = {
            "valor_hora": valor_hora,
            "monto_asistencia_perfecta": monto_asistencia_perfecta,
        }

        response = requests.put(
            f"{BASE_URL}/categorias/{categoria_id}",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al actualizar categoría: {error}",
        }
    
def listar_empleados() -> dict:
    """
    Obtiene la lista de empleados desde el backend.
    """
    try:
        response = requests.get(f"{BASE_URL}/empleados/", timeout=5)
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al listar empleados: {error}",
        }


def crear_empleado(
    nombre: str,
    apellido: str,
    dni: str,
    domicilio: str,
    categoria_id: int,
) -> dict:
    """
    Envía un nuevo empleado al backend.
    """
    try:
        payload = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "domicilio": domicilio,
            "categoria_id": categoria_id,
        }

        response = requests.post(
            f"{BASE_URL}/empleados/",
            json=payload,
            timeout=5,
        )

        # Si backend devuelve error, mostramos su mensaje claro.
        if response.status_code >= 400:
            return {
                "ok": False,
                "message": obtener_mensaje_error(response),
            }

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }

    except Exception as error:
        return {
            "ok": False,
            "message": f"Error de conexión: {error}",
        }
    

def actualizar_empleado(
    empleado_id: int,
    nombre: str,
    apellido: str,
    dni: str,
    domicilio: str,
    categoria_id: int,
    activo: bool,
) -> dict:
    """
    Envía cambios de un empleado existente al backend.
    """
    try:
        payload = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "domicilio": domicilio,
            "categoria_id": categoria_id,
            "activo": activo,
        }

        response = requests.put(
            f"{BASE_URL}/empleados/{empleado_id}",
            json=payload,
            timeout=5,
        )
       # response.raise_for_status()

       
        if response.status_code >= 400:

            return {
                "ok": False,
                "message": obtener_mensaje_error(response),
            }

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al actualizar empleado: {error}",
        }
    
def generar_liquidacion(payload: dict) -> dict:
    """
    Envía datos al backend para generar una liquidación.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/liquidaciones/generar",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        return {
            "ok": True,
            "data": response.json(),
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al generar liquidación: {error}",
        }


def listar_liquidaciones(
    empleado_id: int | None = None,
    mes: int | None = None,
    anio: int | None = None,
) -> dict:
    """
    Obtiene el historial resumido de liquidaciones desde el backend.

    Los filtros son opcionales. Si no se envían, el backend devuelve todas
    las liquidaciones ordenadas de la más reciente a la más antigua.
    """
    try:
        params = {}

        if empleado_id is not None:
            params["empleado_id"] = empleado_id

        if mes is not None:
            params["mes"] = mes

        if anio is not None:
            params["anio"] = anio

        response = requests.get(
            f"{BASE_URL}/liquidaciones/",
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al listar liquidaciones: {error}",
        }


def abrir_pdf_periodo(
    mes: int,
    anio: int,
    empleado_id: int | None = None,
) -> str:
    """
    Devuelve la URL del PDF masivo para un período determinado.
    """
    params = {
        "mes": mes,
        "anio": anio,
    }

    if empleado_id is not None:
        params["empleado_id"] = empleado_id

    query_string = urlencode(params)
    return f"{BASE_URL}/liquidaciones/pdf-periodo?{query_string}"
