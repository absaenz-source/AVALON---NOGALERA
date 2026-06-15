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
# INYECCIÓN DE CSS ULTRA-FORZADO PARA MENÚ LATERAL (TEMA OSCURO)
# ==============================================================================
st.markdown(
    """
    <style>
        /* 1. OCULTAR LOS CÍRCULOS DE RAÍZ */
        div[data-testid="stSidebar"] [data-testid="stWidgetMarkdownTooltipTarget"] {
            display: none !important;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] [data-checked] > div:first-child {
            display: none !important;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] [data-checked] {
            display: flex !important;
            align-items: center !important;
        }

        /* 2. OPCIÓN SELECCIONADA (Fondo iluminado y texto blanco brillante) */
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="true"] {
            background-color: rgba(255, 255, 255, 0.12) !important; 
            border-left: 5px solid #4CAF50 !important; /* Pestaña verde Nogalera */
            border-radius: 6px !important;
            padding: 8px 16px !important;
            margin-bottom: 6px !important;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="true"] label p {
            color: #FFFFFF !important; /* Blanco total */
            font-weight: 700 !important;
        }

        /* 3. OPCIONES NO SELECCIONADAS (Contraste mejorado, color plata visible) */
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="false"] {
            padding: 8px 16px !important;
            margin-bottom: 6px !important;
            border-left: 5px solid transparent !important;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="false"] label p {
            color: #C0CCDA !important; /* Gris plata de alta visibilidad */
            font-weight: 500 !important;
        }

        /* Efecto al pasar el mouse encima */
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="false"]:hover {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border-radius: 6px !important;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] div[data-checked="false"]:hover label p {
            color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 2. FUNCIONES DE BASE DE DATOS (Orden estricto de lectura)
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
# 3. INYECCIÓN DE ESTILOS CSS GLOBALES (Interfaz Premium)
# ==============================================================================
st.markdown(
    """
    <style>
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

    /* Pegar el contenido del panel lateral al borde superior */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }

    /* Eliminar círculos del st.radio en la barra lateral */
    [data-testid="stSidebar"] [data-testid="stRadioButtonCustomComponent"],
    [data-testid="stSidebar"] div.st-ba,
    [data-testid="stSidebar"] .st-bd {
        display: none !important;
    }
    
    /* Diseño de botones redondeados premium en menú lateral */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background-color: transparent !important;
        color: #CBD5E0 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: #CBD5E0 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover p {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] label,
    [data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] label {
        background-color: rgba(255, 255, 255, 0.12) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Estilos estéticos beige para inputs y selectores (Caja principal y dropdown) */
    .stTextInput input, .stNumberInput input, .stDateInput input, 
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div {
        background-color: #FDFBF7 !important;  
        color: #111827 !important;             
        border: 1px solid #E5E7EB !important;  
        border-radius: 6px !important;
    }

    /* Asegurar que el texto dentro del selector activo sea visible y oscuro */
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="select"] span {
        color: #111827 !important;
        font-weight: 500 !important;
    }

    /* Estilizar las opciones cuando el menú se despliega hacia abajo */
    ul[role="listbox"] li {
        background-color: #FDFBF7 !important;
        color: #111827 !important;
    }

    /* Efecto cuando pasas el mouse sobre las opciones desplegadas */
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
# 4. ENCABEZADO GLOBAL ÚNICO (Al tope de la aplicación)
# ==============================================================================
#col_titulo, col_ciclo = st.columns([4, 1])

#with col_titulo:
#    st.markdown("<h2 style='margin: 0; padding: 0; font-family: sans-serif; color: #111827; font-weight: 700;'>Control de Nogalera</h2>", unsafe_allow_html=True)

#with col_ciclo:
#    ciclo_activo = st.selectbox("Ciclo Activo:", options=ciclos_db, label_visibility="collapsed", key="ciclo_header")

#st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 0; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)

# ==============================================================================
# 5. PANEL LATERAL IZQUIERDO (Navegación)
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
# 6. ÁREA CENTRAL DINÁMICA (Navegación limpia)
# ==============================================================================
if opcion_menu == "Dashboard":
    mostrar_dashboard()

elif opcion_menu == "Finanzas":
    mostrar_finanzas()

elif opcion_menu == "Catálogos":
    mostrar_catalogos()