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
# 4. PANEL LATERAL IZQUIERDO (Menú HTML de Alto Contraste)
# ==============================================================================
if "opcion_menu" not in st.session_state:
    st.session_state.opcion_menu = "Dashboard"

with st.sidebar:
    st.image("logo_nogalera.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #111827; font-weight: 700; margin-bottom: 15px; font-size: 14px;'>Navegación</p>", unsafe_allow_html=True)
    
# --- BOTÓN 1: DASHBOARD ---
# Definimos el estilo según si está seleccionado o no
if st.session_state.opcion_menu == "Dashboard":
    estilo_db = "background-color: #2D3142; color: #FFFFFF; font-weight: 700; border: 1px solid #748CAB;"
else:
    estilo_db = "background-color: #4F5D75; color: #111827; font-weight: 600; border: 1px solid #CBD5E1;"

# 1. Inyectamos CSS específico para ESTE botón usando su clave (key) única
st.markdown(f"""
    <style>
    div[data-testid="stButton"] button[key="btn_db"] {{
        {estilo_db}
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 10px; 
        text-align: left; 
        width: 100%;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        transition: all 0.3s ease;
    }}
    /* Efecto hover opcional para mejorar la experiencia visual */
    div[data-testid="stButton"] button[key="btn_db"]:hover {{
        opacity: 0.9;
        border-color: #748CAB;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. El botón ahora ES el contenedor. Al hacerle clic, se ejecuta la acción directamente.
if st.button("📊 Dashboard", use_container_width=True, key="btn_db"):
    st.session_state.opcion_menu = "Dashboard"
    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BOTÓN 2: FINANZAS ---
    if st.session_state.opcion_menu == "Finanzas":
        estilo_fz = "background-color: #2D3142; color: #FFFFFF; font-weight: 700; border: 1px solid #748CAB;"
    else:
        estilo_fz = "background-color: #E2E8F0; color: #FFFFFF; font-weight: 600; border: 1px solid #CBD5E1;"
        
    st.markdown(f"""
        <div style='{estilo_fz} padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: left; cursor: pointer;'>
            <span style='font-size: 16px;'>💵 Finanzas</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("👉 Ir a Finanzas", use_container_width=True, key="btn_fz"):
        st.session_state.opcion_menu = "Finanzas"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BOTÓN 3: CATÁLOGOS ---
    if st.session_state.opcion_menu == "Catálogos":
        estilo_ct = "background-color: #2D3142; color: #FFFFFF; font-weight: 700; border: 1px solid #45A049;"
    else:
        estilo_ct = "background-color: #E2E8F0; color: #111827; font-weight: 600; border: 1px solid #CBD5E1;"
        
    st.markdown(f"""
        <div style='{estilo_ct} padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: left; cursor: pointer;'>
            <span style='font-size: 16px;'>🗂️ Catálogos</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("👉 Ir a Catálogos", use_container_width=True, key="btn_ct"):
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
