from app.core.init_db import init_db

if __name__ == "__main__":
    print("Creando tablas...")
    init_db()
    print("Tablas creadas correctamente")