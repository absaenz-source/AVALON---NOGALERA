import psycopg2
import sys
import streamlit as st
import pandas as pd

def obtener_conexion():
    """Establece la conexión central a la base de datos local de Avalon."""
    # Escudo para evitar que los caracteres de Windows congelen Python
    if sys.platform == 'win32':
        import codecs
        try:
            codecs.lookup('cp65001')
        except LookupError:
            codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
            
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

def obtener_ultimos_ingresos():
    """Trae el historial renombrando las columnas para que finanzas.py las lea perfecto."""
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                fecha AS fecha_op, 
                tipo_ingreso, 
                entidad_origen AS origen_cliente, 
                cuenta_destino, 
                importe_total AS importe_neto 
            FROM ingresos 
            ORDER BY fecha DESC 
            LIMIT 10;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Error al obtener ingresos: {e}")
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

def obtener_ultimos_egresos():
    """Trae los últimos 10 egresos usando los nombres de columna reales de Postgres."""
    try:
        conn = obtener_conexion()
        query = """
            SELECT fecha, categoria_egreso, proveedor_beneficiario, cuenta_origen, importe_total 
            FROM egresos 
            ORDER BY id DESC 
            LIMIT 10;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error al consultar egresos: {e}")
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