import os
import psycopg2
import streamlit as st
import pandas as pd
from database import crear_tabla_presupuestos
from dotenv import load_dotenv
import time
from database import insertar_egreso, insertar_proveedor, consultar_proveedores
from modulos.catalogos import mostrar_catalogos
from modulos.dashboard import mostrar_dashboard
from modulos.finanzas import mostrar_finanzas

# Ejecutamos la función para que revise y si no existe la tabla, la cree en Neon/Localhost
crear_tabla_presupuestos()

# ==============================================================================
# 1. CONFIGURACIONES INICIALES Y VARIABLES DE ENTORNO
# ==============================================================================
load_dotenv()

st.set_page_config(
    page_title="Gestión de Nogalera",
    page_icon="favicon.png",
    layout="wide"
)


# ==============================================================================
# 2. INYECCIÓN DE ESTILOS CSS (Estructura de Pantalla Limpia)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Forzar ancho completo de la aplicación sin márgenes gigantes */
    [data-testid="stAppViewBlockContainer"], 
    .main .block-container {
        padding-top: 1rem !important;  
        padding-left: 2rem !important;   
        padding-right: 2rem !important;  
        max-width: 100% !important;      
        width: 100% !important;
    }

    /* Ocultar la barra superior por estética del ERP */
    [data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 3. FUNCIONES DE BASE DE DATOS (Sincronización central)
# ==============================================================================
def obtener_conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def cargar_ciclos():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_ciclo FROM ciclos ORDER BY id DESC;")
        lista = [fila[0] for fila in cursor.fetchall()]
        cursor.close()
        conn.close()
        return lista
    except Exception as e:
        return []

# Inicializamos la lista de ciclos reales desde la DB
ciclos_db = cargar_ciclos()
if not ciclos_db:
    ciclos_db = ["Ciclo 2026"]


# ==============================================================================
# 4. PANEL LATERAL IZQUIERDO (Navegación Limpia por Estados)
# ==============================================================================
if "opcion_menu" not in st.session_state:
    st.session_state.opcion_menu = "Dashboard"

with st.sidebar:
    st.image("logo_nogalera.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #111827; font-weight: 700; margin-bottom: 5px; font-size: 14px;'>Navegación</p>", unsafe_allow_html=True)
    
    # Botón 1: Dashboard
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.opcion_menu == "Dashboard" else "secondary"):
        st.session_state.opcion_menu = "Dashboard"
        st.rerun()
        
    # Botón 2: Finanzas
    if st.button("💵 Finanzas", use_container_width=True, type="primary" if st.session_state.opcion_menu == "Finanzas" else "secondary"):
        st.session_state.opcion_menu = "Finanzas"
        st.rerun()
        
    # Botón 3: Catálogos
    if st.button("🗂️ Catálogos", use_container_width=True, type="primary" if st.session_state.opcion_menu == "Catálogos" else "secondary"):
        st.session_state.opcion_menu = "Catálogos"
        st.rerun()
    
    st.markdown("""
        <div style='position: fixed; bottom: 15px; left: 15px; color: #4A5568; font-size: 11px; font-family: sans-serif; font-weight: 600;'>
            Nogalera Los Mezquites v1.0
        </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. ÁREA CENTRAL DINÁMICA
# ==============================================================================
if st.session_state.opcion_menu == "Dashboard":
    mostrar_dashboard()

elif st.session_state.opcion_menu == "Finanzas":
    mostrar_finanzas()

elif st.session_state.opcion_menu == "Catálogos":
    mostrar_catalogos()
