import streamlit as st
# Importamos las funciones que ya probamos de tu database
from database import insertar_proveedor, consultar_proveedores
from database import guardar_nuevo_tipo_ingreso, obtener_catalogo_tipos_ingreso, eliminar_tipo_ingreso

def mostrar_catalogos():
    
    
    st.markdown("""
    <style>
        /* Reduce el espacio muerto superior del contenedor principal */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)
    
    
    
    
    st.title("🗂️ Panel de Control - Catálogos Maestros")
    st.write("Administra los conceptos y opciones que alimentan los formularios de Avalon.")
    
    # 1. Definición de las 4 pestañas maestras
    tab_prov, tab_clientes, tab_cuentas, tab_finanzas = st.tabs([
        "👥 Proveedores", 
        "🚜 Clientes",
        "💳 Cuentas Bancarias", 
        "💰 Conceptos de Ingreso"
    ])
    
    # =========================================================================
    # 👥 PESTAÑA: PROVEEDORES
    # =========================================================================
    with tab_prov: 
        st.subheader("➕ Dar de Alta Nuevo Proveedor")
        
        # Formulario de captura de proveedores
        with st.form("form_nuevo_proveedor", clear_on_submit=True):
            nombre_prov = st.text_input("Nombre o Razón Social del Proveedor:*")
            rfc_prov = st.text_input("RFC (Opcional):", max_chars=13)
            tel_prov = st.text_input("Teléfono de Contacto (Opcional):")
            
            btn_guardar_prov = st.form_submit_button("💾 Guardar Proveedor")
            
        if btn_guardar_prov:
            if not nombre_prov.strip():
                st.error("❌ El nombre del proveedor no puede estar vacío.")
            else:
                # Disparamos la función hacia Postgres
                exito = insertar_proveedor(nombre_prov.strip(), rfc_prov.strip(), tel_prov.strip())
                if exito:
                    st.success(f"¡Proveedor **{nombre_prov}** registrado con éxito en Avalon!")
                else:
                    st.error("❌ No se pudo guardar. Es posible que ese proveedor ya exista en el sistema.")

        # --- TABLA DE CONSULTA ABAJO DEL FORMULARIO ---
        st.markdown("---")
        st.subheader("📋 Proveedores Registrados")
        
        df_proveedores = consultar_proveedores()
        
        if df_proveedores is not None and not df_proveedores.empty:
            df_proveedores.columns = ["Nombre / Razón Social", "RFC", "Teléfono", "Fecha de Registro"]
            st.dataframe(df_proveedores, use_container_width=True)
        else:
            st.info("Aún no hay proveedores registrados en el sistema.")

    # =========================================================================
    # 💳 PESTAÑA: CUENTAS BANCARIAS
    # =========================================================================
    with tab_cuentas:
        st.subheader("💳 Cuentas Bancarias")
        st.info("Próximamente: Módulo para dar de alta cuentas de la empresa.")

    # =========================================================================
    # 🚜 PESTAÑA: CLIENTES
    # =========================================================================
    with tab_clientes:
        st.subheader("🚜 Clientes")
        st.info("Próximamente: Módulo para la administración de clientes.")

    # =========================================================================
    # 💰 PESTAÑA NUEVA: CONCEPTOS DE INGRESO
    # =========================================================================
    with tab_finanzas:
        st.subheader("📝 Alta de Nuevos Tipos de Ingreso")
        
        # Formulario de captura para el catálogo de ingresos
        with st.form("form_alta_tipo_ingreso", clear_on_submit=True):
            nuevo_concepto = st.text_input(
                "Nombre del Concepto", 
                placeholder="Ej. VENTA DE MAÍZ, APORTACIÓN EXTRAORDINARIA..."
            )
            
            btn_guardar_concepto = st.form_submit_button("💎 Registrar en Catálogo")
            
        if btn_guardar_concepto:
            if nuevo_concepto.strip():
                exito = guardar_nuevo_tipo_ingreso(nuevo_concepto)
                if exito:
                    st.success(f"¡Excelente! '{nuevo_concepto.upper()}' se agregó correctamente al catálogo.")
                else:
                    st.error("❌ Hubo un problema al guardar. Tal vez el concepto ya existe en Postgres.")
            else:
                st.warning("⚠️ Por favor, escribe un nombre válido antes de guardar.")
                    
        # --- TABLA DE CONSULTA DE CONCEPTOS ---
        st.markdown("---")
        st.markdown("📋 Conceptos de Ingreso Activos en el Sistema")
        
        # Traemos la lista viva desde Postgres
        conceptos_actuales = obtener_catalogo_tipos_ingreso()
        
                    
        # Iteramos cada concepto creando una fila visual con botones
        for concepto in conceptos_actuales:
            # Creamos dos columnas: una ancha para el nombre y una chica para el botón
            col_nombre, col_accion = st.columns([4, 1])
            
            with col_nombre:
                st.markdown(f"🔹 **{concepto}**")
                
            with col_accion:
                # Usamos una clave única (key) combinando el nombre para que Streamlit no se confunda
                btn_eliminar = st.button(f"🗑️", key=f"del_{concepto}")
                
                if btn_eliminar:
                    exito = eliminar_tipo_ingreso(concepto)
                    if exito:
                        st.success(f"Eliminado: {concepto}")
                        # Truco de Streamlit para recargar la pantalla de inmediato y ver el cambio
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar.")