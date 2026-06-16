import streamlit as st
import pandas as pd
# Importamos todas las funciones necesarias desde tu database
from database import (
    insertar_proveedor, consultar_proveedores,
    insertar_cliente, consultar_clientes,
    insertar_cuenta_bancaria, consultar_cuentas_bancarias,
    guardar_nuevo_tipo_ingreso, obtener_catalogo_tipos_ingreso, eliminar_tipo_ingreso
)

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
    st.write("Administra los conceptos y opciones que alimentan los formularios.")
    
    # 1. Definición de las 4 pestañas maestras (Mantenemos tu orden)
    tab_prov, tab_clientes, tab_cuentas, tab_finanzas = st.tabs([
        "👥 Proveedores", 
        "🚜 Clientes",
        "💳 Cuentas Bancarias", 
        "💰 Conceptos de Ingreso"
    ])
    
    # =========================================================================
    # 👥 PESTAÑA: PROVEEDORES (Código Original)
    # =========================================================================
    with tab_prov: 
        st.subheader("➕ Dar de Alta Nuevo Proveedor")
        
        with st.form("form_nuevo_proveedor", clear_on_submit=True):
            nombre_prov = st.text_input("Nombre o Razón Social del Proveedor:*")
            rfc_prov = st.text_input("RFC (Opcional):", max_chars=13)
            tel_prov = st.text_input("Teléfono de Contacto (Opcional):")
            
            btn_guardar_prov = st.form_submit_button("💾 Guardar Proveedor")
            
        if btn_guardar_prov:
            if not nombre_prov.strip():
                st.error("❌ El nombre del proveedor no puede estar vacío.")
            else:
                exito = insertar_proveedor(nombre_prov.strip(), rfc_prov.strip(), tel_prov.strip())
                if exito:
                    st.success(f"¡Proveedor **{nombre_prov}** registrado con éxito en Avalon!")
                    st.rerun()
                else:
                    st.error("❌ No se pudo guardar. Es posible que ese proveedor ya exista en el sistema.")

        st.markdown("---")
        st.subheader("📋 Proveedores Registrados")
        
        df_proveedores = consultar_proveedores()
        if df_proveedores is not None and not df_proveedores.empty:
            df_proveedores.columns = ["Nombre / Razón Social", "RFC", "Teléfono", "Fecha de Registro"]
            st.dataframe(df_proveedores, use_container_width=True)
        else:
            st.info("Aún no hay proveedores registrados en el sistema.")

    # =========================================================================
    # 🚜 PESTAÑA: CLIENTES (¡Activada!)
    # =========================================================================
    with tab_clientes:
        st.subheader("➕ Dar de Alta Nuevo Cliente")
        
        with st.form("form_nuevo_cliente", clear_on_submit=True):
            nombre_cte = st.text_input("Nombre o Razón Social del Cliente:*", placeholder="Ej. Comercializadora de Granos...")
            rfc_cte = st.text_input("RFC del Cliente (Opcional):", max_chars=13, placeholder="XAXX010101000")
            tel_cte = st.text_input("Teléfono de Contacto (Opcional):", placeholder="625XXXXXXX")
            
            btn_guardar_cte = st.form_submit_button("💾 Guardar Cliente")
            
        if btn_guardar_cte:
            if not nombre_cte.strip():
                st.error("❌ El nombre del cliente no puede estar vacío.")
            else:
                exito = insertar_cliente(nombre_cte, rfc_cte, tel_cte)
                if exito:
                    st.success(f"¡Cliente **{nombre_cte.upper()}** registrado con éxito!")
                    st.rerun()
                else:
                    st.error("❌ No se pudo guardar el cliente en el sistema.")

        st.markdown("---")
        st.subheader("📋 Clientes Registrados")
        
        df_clientes = consultar_clientes()
        if df_clientes is not None and not df_clientes.empty:
            df_clientes.columns = ["Nombre / Razón Social", "RFC", "Teléfono", "Fecha de Registro"]
            st.dataframe(df_clientes, use_container_width=True)
        else:
            st.info("Aún no hay clientes registrados en el sistema.")

    # =========================================================================
    # 💳 PESTAÑA: CUENTAS BANCARIAS (¡Activada!)
    # =========================================================================
    with tab_cuentas:
        st.subheader("➕ Registrar Cuenta Bancaria o Fondo")
        
        with st.form("form_nueva_cuenta", clear_on_submit=True):
            nombre_cta = st.text_input("Nombre Identificador de la Cuenta:*", placeholder="Ej. BBVA Principal, Caja Chica...")
            banco_cta = st.text_input("Institución Bancaria / Ubicación:*", placeholder="Ej. BBVA, Santander, Efectivo")
            tipo_cta = st.selectbox("Tipo de Cuenta:*", ["Débito / Chequera", "Crédito", "Efectivo / Caja"])
            
            btn_guardar_cta = st.form_submit_button("💾 Guardar Cuenta")
            
        if btn_guardar_cta:
            if not nombre_cta.strip() or not banco_cta.strip():
                st.error("❌ El Nombre de la Cuenta y la Institución Bancaria son campos obligatorios.")
            else:
                exito = insertar_cuenta_bancaria(nombre_cta, banco_cta, tipo_cta)
                if exito:
                    st.success(f"¡Cuenta **{nombre_cta.upper()}** dada de alta exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ Hubo un error al intentar guardar la cuenta.")

        st.markdown("---")
        st.subheader("📋 Cuentas Configuradas")
        
        df_cuentas = consultar_cuentas_bancarias()
        if df_cuentas is not None and not df_cuentas.empty:
            df_cuentas.columns = ["Identificador de Cuenta", "Banco / Origen", "Tipo"]
            st.dataframe(df_cuentas, use_container_width=True)
        else:
            st.info("Aún no hay cuentas configuradas en el sistema.")

    # =========================================================================
    # 💰 PESTAÑA: CONCEPTOS DE INGRESO (Código Original Integrado)
    # =========================================================================
    with tab_finanzas:
        st.subheader("📝 Alta de Nuevos Tipos de Ingreso")
        
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
                    st.rerun()
                else:
                    st.error("❌ Hubo un problema al guardar. Tal vez el concepto ya existe en Postgres.")
            else:
                st.warning("⚠️ Por favor, escribe un nombre válido antes de guardar.")
                    
        st.markdown("---")
        st.markdown("📋 Conceptos de Ingreso Activos en el Sistema")
        
        conceptos_actuales = obtener_catalogo_tipos_ingreso()
        
        for concepto in conceptos_actuales:
            col_nombre, col_accion = st.columns([4, 1])
            with col_nombre:
                st.markdown(f"🔹 **{concepto}**")
                
            with col_accion:
                btn_eliminar = st.button(f"🗑️", key=f"del_{concepto}")
                if btn_eliminar:
                    exito = eliminar_tipo_ingreso(concepto)
                    if exito:
                        st.success(f"Eliminado: {concepto}")
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar.")