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
# 2. INYECCIÓN DE ESTILOS CSS UNIFICADOS (Tema Claro de Alta Legibilidad)
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

    /* Forzar a la pantalla principal a usar el 100% del ancho físico */
    [data-testid="stAppViewBlockContainer"], 
    .main .block-container,
    .st-emotion-cache-1z16p0t {
        padding-top: 0.5rem !important;  
        padding-left: 2rem !important;   
        padding-right: 2rem !important;  
        max-width: 100% !important;      
        width: 100% !important;
    }

    /* Ocultar la barra superior nativa de Streamlit */
    [data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }

    /* ============================================================================== */
    /* DISEÑO EXCLUSIVO PARA LA BARRA LATERAL (SIDEBAR) CLARA Y PREMIUM */
    /* ============================================================================== */

/* ============================================================================== */
    /* CONTROL TOTAL DEL ST.RADIO EN EL MENÚ LATERAL (Contraste Máximo) */
    /* ============================================================================== */
    
    /* 1. Forzar color oscuro en los textos de las opciones NO seleccionadas */
    [data-testid="stSidebar"] [role="radiogroup"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] label span,
    div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="false"] label p {
        color: #1A252F !important; /* Gris carbón/Negro de alta visibilidad */
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* 2. Efecto Hover: Cuando pasas el mouse encima de las opciones */
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background-color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover p {
        color: #000000 !important; /* Negro puro al pasar el mouse */
    }

    /* 3. OPCIÓN SELECCIONADA ACTIVA (Fondo marcado y letra negra brillante) */
    [data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] label,
    [data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] label,
    div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="true"] {
        background-color: #DDE2E5 !important; /* Fondo gris medio que hace contraste */
        border-left: 5px solid #4CAF50 !important; /* Tu pestaña verde de la Nogalera */
        border-radius: 8px !important;
    }
    
    /* Texto de la opción que está activa actualmente */
    [data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] label p,
    div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="true"] label p {
        color: #000000 !important; /* Negro absoluto */
        font-weight: 700 !important;
    }







    
    /* ============================================================================== */
    /* ENTRADAS DE DATOS Y FORMULARIOS COHESIVOS */
    /* ============================================================================== */
    .stTextInput input, .stNumberInput input, .stDateInput input, 
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div {
        background-color: #FDFBF7 !important;  
        color: #111827 !important;              
        border: 1px solid #E5E7EB !important;  
        border-radius: 6px !important;
    }

    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="select"] span {
        color: #111827 !important;
        font-weight: 500 !important;
    }

    ul[role="listbox"] li {
        background-color: #FDFBF7 !important;
        color: #111827 !important;
    }

    ul[role="listbox"] li:hover {
        background-color: #F3F4F6 !important;
    }

    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        padding: 2rem !important;
        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 2px !important;
        padding-top: 10px;
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
# 4. PANEL LATERAL IZQUIERDO (Navegación limpia)
# ==============================================================================
with st.sidebar:
    st.image("logo_nogalera.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    opcion_menu = st.radio(
        "Navegación",
        [
            "Dashboard", 
            "Finanzas", 
            "Catálogos"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("""
        <div style='position: fixed; bottom: 15px; left: 15px; color: #718096; font-size: 11px; font-family: sans-serif;'>
            Nogalera Los Mezquites v1.0
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 5. ÁREA CENTRAL DINÁMICA
# ==============================================================================
if opcion_menu == "Dashboard":
    mostrar_dashboard()

elif opcion_menu == "Finanzas":
    mostrar_finanzas()

elif opcion_menu == "Catálogos":
    mostrar_catalogos()
