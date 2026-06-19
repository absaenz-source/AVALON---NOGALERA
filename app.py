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
# 2. INYECCIÓN DE ESTILOS CSS UNIFICADOS (Contraste Absoluto para Botones)
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. Fondo principal de la app y textos generales */
    .stApp {
        background-color: #F8F9FA !important;
        color: #212529 !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #212529 !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="marker-cluster"] {
        color: #212529 !important;
    }

    /* Ancho completo de la app */
    [data-testid="stAppViewBlockContainer"], 
    .main .block-container {
        padding-top: 0.5rem !important;  
        padding-left: 2rem !important;   
        padding-right: 2rem !important;  
        max-width: 100% !important;      
        width: 100% !important;
    }

    /* Ocultar barra superior */
    [data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }

    /* Fondo de la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #F1F3F5 !important; 
        border-right: 1px solid #E0E0E0 !important;
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }

    /* ============================================================================== */
    /* EL TRUCO DEFINITIVO: ESTILO FORZADO PARA NUESTROS BOTONES DEL MENÚ */
    /* ============================================================================== */
    
    /* Forzar que CUALQUIER botón dentro del sidebar tenga texto oscuro y fondo visible */
    [data-testid="stSidebar"] button {
        background-color: #E2E8F0 !important; /* Fondo gris claro bien definido */
        border: 1px solid #CBD5E1 !important; /* Borde sutil */
        border-radius: 8px !important;
        padding: 10px 16px !important;
        margin-bottom: 2px !important;
        transition: all 0.2s ease !important;
    }

    /* Forzar el color del texto e íconos a NEGRO ABSOLUTO para que sea ultra legible */
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] button span,
    [data-testid="stSidebar"] button div {
        color: #111827 !important; 
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* Efecto cuando pasas el mouse por encima (Hover) */
    [data-testid="stSidebar"] button:hover {
        background-color: #CBD5E1 !important; /* Se oscurece el fondo al pasar el mouse */
        border-color: #94A3B8 !important;
    }

    /* Cuando el botón corresponde a la pestaña ACTIVA (Primary de Streamlit) */
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #4CAF50 !important; /* Verde Nogalera */
        border-color: #45A049 !important;
    }
    [data-testid="stSidebarUserContent"] button[kind="primary"] p {
        color: #FFFFFF !important; /* Texto blanco brillante solo si está activo */
    }

    /* Inputs de datos beige del área central */
    .stTextInput input, .stNumberInput input, .stDateInput input, 
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div {
        background-color: #FDFBF7 !important;  
        color: #111827 !important;              
        border: 1px solid #E5E7EB !important;  
        border-radius: 6px !important;
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
