"""Configuracion central de la aplicacion."""

import os
from pathlib import Path

from dotenv import load_dotenv


# Buscamos el archivo .env en la raiz del proyecto para centralizar la carga
# de variables de entorno desde un unico lugar.
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

# Cargamos las variables del archivo .env si existe. Si no existe, Python
# seguira usando las variables definidas en el entorno del sistema.
load_dotenv(dotenv_path=ENV_FILE)

# Exponemos la URL de conexion a la base de datos para reutilizarla en el resto
# de la aplicacion. Si no esta definida, devolvemos una cadena vacia.
#DATABASE_URL = os.getenv("DATABASE_URL", "") original cambiada por recomendacion de chat 
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env")