import os
import psycopg2
import sys
import streamlit as st
import pandas as pd
from dotenv import load_dotenv


# Cargar el archivo .env por si acaso estás en local
load_dotenv()

def obtener_conexion():
    """Establece la conexión a Postgres de forma dinámica para Local o Web."""
    # 1. Intentamos leer los Secrets de Streamlit Cloud (Si estamos en la Web)
    if "DB_HOST" in st.secrets:
        host = st.secrets["DB_HOST"]
        database = st.secrets["DB_NAME"]
        user = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
    # 2. Si no existen (estamos en tu computadora), leemos el archivo .env local
    else:
        host = os.getenv("DB_HOST", "localhost")
        database = os.getenv("DB_NAME", "avalon_db")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "tu_password_local")

    # Ejecutamos la conexión con las variables dinámicas
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        connect_timeout=3
    )


def obtener_conexion():
    """Establece la conexión central a la base de datos local de Avalon."""
    # Escudo para evitar que los caracteres de Windows congelen Python
    
    
    host = os.getenv("DB_HOST") or st.secrets.get("DB_HOST")
    database = os.getenv("DB_NAME") or st.secrets.get("DB_NAME")
    user = os.getenv("DB_USER") or st.secrets.get("DB_USER")
    password = os.getenv("DB_PASSWORD") or st.secrets.get("DB_PASSWORD")
    
                
    return psycopg2.connect(
        host="localhost",
        database="avalon_db",
        user="postgres",
        password="baretta",  # Tu contraseña real local
        port="5432",
        connect_timeout=3
    )












# ==============================================================================
# 💰 SECCIÓN: INGRESOS
# ==============================================================================

def guardar_ingreso(tipo_ingreso, fecha_op, folio_ref, origen_cliente, tipo_moneda, cuenta_destino, ciclo_produc, importe_neto, observaciones):
    """Inserta un nuevo registro de ingreso usando las columnas reales de Postgres."""
    try:
        conn = obtener_conexion() 
        cur = conn.cursor()
        
        insert_query = """
            INSERT INTO ingresos (
                tipo_ingreso, fecha, folio, entidad_origen, moneda, 
                cuenta_destino, ciclo_productivo, importe_total, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        cur.execute(insert_query, (
            tipo_ingreso, fecha_op, folio_ref, origen_cliente, tipo_moneda, 
            cuenta_destino, ciclo_produc, importe_neto, observaciones
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error detallado al guardar ingreso: {e}")
        return False




def obtener_ultimos_ingresos(ciclo="Ciclo 2026"):
    """Trae el historial de ingresos filtrado por ciclo incluyendo el ID único."""
    conn = obtener_conexion()
    if not conn:
        return None
    try:
        # Añadimos el id y el filtro del ciclo
        query = """
            SELECT id, tipo_ingreso, fecha_op, folio_referencia, origen_cliente, 
                   tipo_moneda, cuenta_destino, ciclo_productivo, importe_neto, observaciones 
            FROM ingresos 
            WHERE ciclo_productivo = %s
            ORDER BY fecha_op DESC, id DESC;
        """
        df = pd.read_sql(query, conn, params=(ciclo,))
        conn.close()
        return df
    except Exception as e:
        print(f"Error al obtener últimos ingresos: {e}")
        return None


# ==============================================================================
# 📉 SECCIÓN: EGRESOS
# ==============================================================================

def guardar_egreso(categoria_egreso, fecha, folio, proveedor_beneficiario, moneda, cuenta_origen, ciclo_productivo, importe_total, observaciones):
    """Inserta un nuevo registro de gasto haciendo match exacto con las columnas reales de Postgres."""
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        query = """
            INSERT INTO egresos (
                fecha, categoria_egreso, folio, proveedor_beneficiario, 
                moneda, cuenta_origen, ciclo_productivo, importe_total, observaciones
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (
            fecha, categoria_egreso, folio, proveedor_beneficiario, 
            moneda, cuenta_origen, ciclo_productivo, importe_total, observaciones
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al guardar el egreso: {e}")
        return False



def obtener_ultimos_egresos(ciclo="Ciclo 2026"):
    """Trae el historial de egresos filtrado por ciclo incluyendo el ID único."""
    conn = obtener_conexion()
    if not conn:
        return None
    try:
        query = """
            SELECT id, categoria_egreso, fecha, folio, proveedor_beneficiario, 
                   moneda, cuenta_origen, ciclo_productivo, importe_total, observaciones 
            FROM egresos 
            WHERE ciclo_productivo = %s
            ORDER BY fecha DESC, id DESC;
        """
        df = pd.read_sql(query, conn, params=(ciclo,))
        conn.close()
        return df
    except Exception as e:
        print(f"Error al obtener últimos egresos: {e}")
        return None



# 🔄 PUENTES DE COMPATIBILIDAD
# Mapeamos los nombres viejos a las funciones nuevas para que app.py no truene al importar
insertar_egreso = guardar_egreso


# ==============================================================================
# 👥 SECCIÓN: CATÁLOGOS / PROVEEDORES
# ==============================================================================

def insertar_proveedor(nombre, rfc, telefono):
    """Inserta un nuevo proveedor en la base de datos."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO proveedores (nombre_proveedor, rfc, telefono)
            VALUES (%s, %s, %s);
        """
        valores = (nombre, rfc, telefono)
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        try:
            error_limpio = str(e).encode('utf-8', errors='ignore').decode('latin-1', errors='ignore')
        except Exception:
            error_limpio = str(e)
            
        st.error(f"PostgreSQL rechazó el registro. Motivo: {error_limpio}")
        return False
    
def consultar_proveedores():
    """Trae la lista completa de proveedores ordenados por el más reciente."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = "SELECT nombre_proveedor, rfc, telefono, fecha_registro FROM proveedores ORDER BY id DESC;"
        cursor.execute(query)
        
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return pd.DataFrame(datos, columns=columnas)
    except Exception as e:
        print(f"⚠️ Error al consultar proveedores: {e}")
        return None

def obtener_catalogo_tipos_ingreso():
    """Trae la lista dinámica de tipos de ingreso desde la base de datos."""
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM cat_tipos_ingreso ORDER BY nombre ASC;")
        opciones = [fila[0] for fila in cur.fetchall()]
        cur.close()
        conn.close()
        
        return opciones if opciones else ["VENTA DE NUEZ"]
    except Exception as e:
        print(f"⚠️ Error al obtener catálogo de tipos de ingreso: {e}")
        return ["VENTA DE NUEZ"]
    
def guardar_nuevo_tipo_ingreso(nombre_concepto):
    """Inserta un nuevo concepto en el catálogo de tipos de ingreso, pasándolo a mayúsculas."""
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        concepto_upper = nombre_concepto.strip().upper()
        query = "INSERT INTO cat_tipos_ingreso (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING;"
        cur.execute(query, (concepto_upper,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error al guardar en catálogo de ingresos: {e}")
        return False

def eliminar_tipo_ingreso(nombre_concepto):
    """Elimina un concepto específico del catálogo de tipos de ingreso."""
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        query = "DELETE FROM cat_tipos_ingreso WHERE nombre = %s;"
        cur.execute(query, (nombre_concepto,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error al eliminar del catálogo de ingresos: {e}")
        return False

# ==============================================================================
# 📊 SECCIÓN: PRESUPUESTOS
# ==============================================================================
    
def crear_tabla_presupuestos():
    """Genera la estructura de la tabla de presupuestos si no existe."""
    try:
        conn = obtener_conexion()
        cursor = cursor = conn.cursor()
        
        query = """
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                ciclo INT NOT NULL,
                concepto VARCHAR(50) NOT NULL,
                monto_estimado NUMERIC(12, 2) NOT NULL,
                UNIQUE(ciclo, concepto)
            );
        """
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error al crear tabla presupuestos: {e}")
        return False

def guardar_presupuesto(ciclo, concepto, monto):
    """Guarda o actualiza montos proyectados."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO budgets (ciclo, concepto, monto_estimado)
            VALUES (%s, %s, %s)
            ON CONFLICT (ciclo, concepto) 
            DO UPDATE SET monto_estimado = EXCLUDED.monto_estimado;
        """
        valores = (ciclo, concepto, monto)
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error al guardar presupuesto para {concepto}: {e}")
        return False
    




def obtener_totales_por_cuenta(ciclo="Ciclo 2026"):
    """Suma ingresos y egresos por cuenta y calcula totales globales con mapeo estricto."""
    conn = obtener_conexion() 
    
    datos = {
        "BBVA": {"ingresos": 0.0, "egresos": 0.0},
        "Efectivo": {"ingresos": 0.0, "egresos": 0.0},
        "Otras": {"ingresos": 0.0, "egresos": 0.0}, # Cuenta de respaldo para capturar el limbo
        "total_ingresos_global": 0.0,
        "total_egresos_global": 0.0
    }
    
    if not conn:
        return datos
    
    try:
        cur = conn.cursor()
        
        # 1. Sumar ingresos por cuenta_destino
        cur.execute("""
            SELECT COALESCE(TRIM(cuenta_destino), 'No Especificado'), COALESCE(SUM(importe_total), 0) 
            FROM ingresos 
            WHERE ciclo_productivo = %s 
            GROUP BY cuenta_destino;
        """, (ciclo,))
        ingresos_raw = cur.fetchall()
        
        # 2. Sumar egresos por cuenta_origen
        cur.execute("""
            SELECT COALESCE(TRIM(cuenta_origen), 'No Especificado'), COALESCE(SUM(importe_total), 0) 
            FROM egresos 
            WHERE ciclo_productivo = %s 
            GROUP BY cuenta_origen;
        """, (ciclo,))
        egresos_raw = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Procesar Ingresos
        for cuenta, total in ingresos_raw:
            valor = float(total)
            datos["total_ingresos_global"] += valor
            
            nombre_limpio = cuenta.lower()
            if "bbva" in nombre_limpio or "6658" in nombre_limpio:
                datos["BBVA"]["ingresos"] += valor
            elif "efectivo" in nombre_limpio or "efec" in nombre_limpio:
                datos["Efectivo"]["ingresos"] += valor
            else:
                datos["Otras"]["ingresos"] += valor # Captura nombres extraños
                
        # Procesar Egresos
        for cuenta, total in egresos_raw:
            valor = float(total)
            datos["total_egresos_global"] += valor
            
            nombre_limpio = cuenta.lower()
            if "bbva" in nombre_limpio or "6658" in nombre_limpio:
                datos["BBVA"]["egresos"] += valor
            elif "efectivo" in nombre_limpio or "efec" in nombre_limpio:
                datos["Efectivo"]["egresos"] += valor
            else:
                datos["Otras"]["egresos"] += valor
                
        return datos
        
    except Exception as e:
        print(f"Error al obtener totales por cuenta: {e}")
        return datos


def obtener_gastos_por_categoria(ciclo="Ciclo 2026"):
    """Trae el desglose real de egresos acumulados por categoría."""
    conn = obtener_conexion()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT categoria_egreso, COALESCE(SUM(importe_total), 0) AS total
            FROM egresos
            WHERE ciclo_productivo = %s
            GROUP BY categoria_egreso
            ORDER BY total DESC;
        """, (ciclo,))
        
        filas = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convertir a un diccionario clásico { "Insumos": 5000.00, ... }
        return {cat: float(total) for cat, total in filas}
        
    except Exception as e:
        print(f"Error al obtener gastos por categoría: {e}")
        return {}


def eliminar_registro_db(tabla, id_registro):
    """Elimina un registro específico por su ID en la tabla indicada (ingresos o egresos)."""
    conn = obtener_conexion()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # Asegúrate de que tu columna llave primaria en Postgres se llame 'id'
        cur.execute(f"DELETE FROM {tabla} WHERE id = %s;", (id_registro,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al eliminar en la tabla {tabla}: {e}")
        return False

def actualizar_ingreso_db(id_registro, datos_nuevos):
    """Actualiza las columnas modificadas de un ingreso específico."""
    conn = obtener_conexion()
    if not conn or not datos_nuevos:
        return False
    try:
        cur = conn.cursor()
        for columna, valor in datos_nuevos.items():
            # Construcción dinámica segura para actualizar solo lo que cambió
            cur.execute(f"UPDATE ingresos SET {columna} = %s WHERE id = %s;", (valor, id_registro))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar ingreso: {e}")
        return False

def actualizar_egreso_db(id_registro, datos_nuevos):
    """Actualiza las columnas modificadas de un egreso específico."""
    conn = obtener_conexion()
    if not conn or not datos_nuevos:
        return False
    try:
        cur = conn.cursor()
        for columna, valor in datos_nuevos.items():
            cur.execute(f"UPDATE egresos SET {columna} = %s WHERE id = %s;", (valor, id_registro))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar egreso: {e}")
        return False
    
    


def crear_tablas_catalogos_faltantes():
    """Crea las tablas de contactos (clientes/proveedores) y cuentas si no existen."""
    conn = obtener_conexion()
    if not conn: return
    try:
        cur = conn.cursor()
        # 1. Tabla de Contactos (Clientes y Proveedores)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contactos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                tipo VARCHAR(20) NOT NULL, -- 'CLIENTE', 'PROVEEDOR', 'AMBOS'
                rfc VARCHAR(13),
                telefono VARCHAR(20),
                observaciones TEXT
            );
        """)
        # 2. Tabla de Cuentas Bancarias / Efectivo
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cuentas_bancarias (
                id SERIAL PRIMARY KEY,
                nombre_cuenta VARCHAR(100) NOT NULL, -- 'BBVA', 'SANTANDER', 'EFECTIVO CHICA', etc.
                institucion VARCHAR(100),            -- 'BBVA', 'Santander', 'Caja Fuerte'
                tipo_cuenta VARCHAR(30),             -- 'DEBITO', 'CREDITO', 'EFECTIVO'
                divisa VARCHAR(10) DEFAULT 'MXN'     -- 'MXN', 'USD'
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al crear tablas de catálogos: {e}")

# Funciones para el Catálogo de Contactos
def guardar_contacto(nombre, tipo, rfc, telefono, observaciones):
    conn = obtener_conexion()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contactos (nombre, tipo, rfc, telefono, observaciones)
            VALUES (%s, %s, %s, %s, %s);
        """, (nombre.upper().strip(), tipo, rfc.upper().strip(), telefono, observaciones))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        return False

# Funciones para el Catálogo de Cuentas
def guardar_cuenta_bancaria(nombre_cuenta, institucion, tipo_cuenta, divisa):
    conn = obtener_conexion()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cuentas_bancarias (nombre_cuenta, institucion, tipo_cuenta, divisa)
            VALUES (%s, %s, %s, %s);
        """, (nombre_cuenta.upper().strip(), institucion.upper().strip(), tipo_cuenta, divisa))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al guardar cuenta bancaria: {e}")
        return False
    
    
import pandas as pd # Asegúrate de que esté importado al inicio de database.py

def insertar_cliente(nombre, rfc, telefono):
    """Inserta un nuevo cliente en la base de datos."""
    conn = obtener_conexion() # Usa la función de conexión que tengas en tu archivo
    if not conn: return False
    try:
        cur = conn.cursor()
        # Asegúrate de tener una tabla llamada 'clientes' o créala en Postgres si hace falta
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                rfc VARCHAR(13),
                telefono VARCHAR(20),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            INSERT INTO clientes (nombre, rfc, telefono) 
            VALUES (%s, %s, %s);
        """, (nombre.upper().strip(), rfc.upper().strip(), telefono.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al insertar cliente: {e}")
        return False

def consultar_clientes():
    """Devuelve un DataFrame con todos los clientes registrados."""
    conn = obtener_conexion()
    if not conn: return None
    try:
        query = "SELECT nombre, rfc, telefono, fecha_registro FROM clientes ORDER BY nombre ASC;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al consultar clientes: {e}")
        return None

def insertar_cuenta_bancaria(nombre_cuenta, banco, tipo_cuenta):
    """Inserta una nueva cuenta o fondo de caja."""
    conn = obtener_conexion()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cuentas_bancarias (
                id SERIAL PRIMARY KEY,
                nombre_cuenta VARCHAR(100) NOT NULL,
                banco VARCHAR(100) NOT NULL,
                tipo_cuenta VARCHAR(50),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            INSERT INTO cuentas_bancarias (nombre_cuenta, banco, tipo_cuenta) 
            VALUES (%s, %s, %s);
        """, (nombre_cuenta.upper().strip(), banco.upper().strip(), tipo_cuenta))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al insertar cuenta: {e}")
        return False

def consultar_cuentas_bancarias():
    """Devuelve un DataFrame con las cuentas activas."""
    conn = obtener_conexion()
    if not conn: return None
    try:
        query = "SELECT nombre_cuenta, banco, tipo_cuenta FROM cuentas_bancarias ORDER BY nombre_cuenta ASC;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al consultar cuentas: {e}")
        return None