import requests


#BASE_URL = "http://127.0.0.1:8000"
BASE_URL = "http://68.183.139.118:8000"


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
        response.raise_for_status()

        data = response.json()
        return {
            "ok": True,
            "data": data,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Error al crear empleado: {error}",
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