import os
import psycopg2
from dotenv import load_dotenv

# 1. Cargar las variables del archivo .env
load_dotenv()

def probar_conexion():
    try:
        # 2. Intentar conectar a Neon con tus credenciales
        print("Intentando conectar a la base de datos en Neon...")
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        # 3. Crear un cursor para interactuar con la DB
        cursor = conexion.cursor()
        
        # Ejecutar una consulta simple para verificar que las tablas existan
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        
        tablas = cursor.fetchall()
        
        print("\n¡CONEXIÓN EXITOSA! 🎉")
        print("Tablas encontradas en tu base de datos:")
        for tabla in tablas:
            print(f" - {tabla[0]}")
            
        # Cerrar la comunicación
        cursor.close()
        conexion.close()
        
    except Exception as error:
        print("\n❌ Error al conectar a la base de datos:")
        print(error)

if __name__ == "__main__":
    probar_conexion()