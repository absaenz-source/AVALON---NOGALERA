import streamlit as st
from datetime import datetime
import pandas as pd
# Importamos exactamente tus funciones de base de datos
from database import (
    obtener_catalogo_tipos_ingreso, 
    guardar_ingreso, 
    obtener_ultimos_ingresos, 
    guardar_egreso, 
    obtener_ultimos_egresos,
    obtener_totales_por_cuenta,
    obtener_gastos_por_categoria,
    eliminar_registro_db,      # <-- Nueva
    actualizar_ingreso_db,     # <-- Nueva
    actualizar_egreso_db
     
)

def mostrar_finanzas():
    
    # Reducción de espacios superiores para estética
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("💸 Gestión Financiera y Flujo de Caja")
    st.write("Registra y audita los movimientos económicos etiquetados por ciclo productivo.")

    # Creamos las 3 pestañas principales
    tab1, tab2, = st.tabs(["💰 Registrar Ingreso", "📉 Registrar Egreso"])
    
    # =========================================================================
    # 💰 PESTAÑA 1: REGISTRAR INGRESO
    # =========================================================================
    with tab1:
        st.subheader("📝 Formulario de Captura de Ingresos")
        
        opciones_catalogo = obtener_catalogo_tipos_ingreso()
        tipo_ingreso = st.selectbox("🎯 Tipo de Ingreso", opciones_catalogo, key="fin_ing_tipo_sel")
        
        c1, c2 = st.columns(2)
        with c1:
            fecha_op = st.date_input("Fecha de Operación", datetime.now(), key="fin_ing_fecha_input")
            folio_ref = st.text_input("Folio / Referencia", placeholder="Ej: Folio SAT o 'SF'", key="fin_ing_folio_input")
            origen_cliente = st.text_input("Origen / Cliente / Institución", placeholder="Nombre del pagador", key="fin_ing_origen_input")
        
        with c2:
            tipo_moneda = st.selectbox("Tipo de Moneda", ["MXN", "USD"], key="fin_ing_moneda_sel")
            # HOMOLOGADO: Nombres limpios coincidentes con egresos
            cuenta_destino = st.selectbox("Cuenta de Destino (Entrada)", ["BBVA", "SANTANDER", "EFECTIVO"], key="fin_ing_cuenta_sel")
            ciclo_produc = st.selectbox("Ciclo Productivo Imputable", ["Ciclo 2026", "Ciclo 2025"], key="fin_ing_ciclo_sel")
        
        # Lógica dinámica para cálculo de Nuez / Entrada General
        c3, c4 = st.columns(2)
        with c3:
            if tipo_ingreso == "VENTA DE NUEZ":
                kilogramos = st.number_input("Cantidad (Kg):", min_value=0.0, step=1.0, value=0.0, key="fin_ing_nuez_kg")
                precio_por_kg = st.number_input("Precio por Kg (MXN):", min_value=0.0, step=0.50, value=0.0, key="fin_ing_nuez_precio")
                
                importe_neto = kilogramos * precio_por_kg
                st.number_input("Importe Neto Calculado ($):", value=importe_neto, disabled=True, key="fin_ing_nuez_calc_dis")
            else:
                importe_neto = st.number_input("Importe Neto ($):", min_value=0.0, step=100.0, value=0.0, key="fin_ing_monto_manual")
        
        with c4:
            observaciones = st.text_area("Observaciones adicionales", placeholder="Detalles del movimiento...", height=140, key="fin_ing_obs_input")
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_guardar = st.button("💎 Registrar Ingreso en Avalon", key="fin_ing_btn_guardar")
        
        if boton_guardar:
            if importe_neto > 0:
                exito = guardar_ingreso(
                    tipo_ingreso, fecha_op, folio_ref, origen_cliente, 
                    tipo_moneda, cuenta_destino, ciclo_produc, importe_neto, observaciones
                )
                if exito:
                    st.success(f"✅ ¡Ingreso por ${importe_neto:,.2f} registrado con éxito!")
                    st.rerun()
                else:
                    st.error("❌ Error al conectar con la base de datos.")
            else:
                st.warning("⚠️ El importe debe ser mayor a $0.00 para poder registrarse.")
           
        
        
        
        # --- TABLA DE HISTORIAL DE INGRESOS EDITABLE ---
        st.markdown("---")
        st.subheader("📜 Historial de Ingresos (Editable)")
        st.caption("💡 Haz doble clic en cualquier celda para modificar. Para borrar, selecciona la fila completa del lado izquierdo y presiona la tecla 'Supr' o 'Delete' en tu teclado, luego dale al botón Guardar Cambios.")
        
        df_ingresos = obtener_ultimos_ingresos("Ciclo 2026")
        
        if df_ingresos is not None and not df_ingresos.empty:
            # st.data_editor habilita la edición interactiva
            ingresos_editados = st.data_editor(
                df_ingresos,
                num_rows="dynamic", # Permite eliminar filas seleccionándolas
                disabled=["id"],    # Bloqueamos el ID para que no se pueda alterar
                column_config={
                    "importe_neto": st.column_config.NumberColumn("Importe", format="$%,.2f"),
                    "fecha_op": st.column_config.DateColumn("Fecha"),
                },
                use_container_width=True,
                key="editor_ingresos_key"
            )
            
            # Botón para procesar los cambios hechos en la tabla
            if st.button("💾 Guardar Cambios en Ingresos", key="btn_save_ing"):
                cambios = st.session_state["editor_ingresos_key"]
                exito_total = True
                
                # 1. Procesar filas eliminadas
                if cambios["deleted_rows"]:
                    for indice_fila in cambios["deleted_rows"]:
                        id_a_borrar = df_ingresos.iloc[indice_fila]["id"]
                        if not eliminar_registro_db("ingresos", int(id_a_borrar)):
                            exito_total = False
                
                # 2. Procesar filas modificadas
                if cambios["edited_rows"]:
                    for indice_fila, columnas_cambiadas in cambios["edited_rows"].items():
                        id_a_editar = df_ingresos.iloc[int(indice_fila)]["id"]
                        if not actualizar_ingreso_db(int(id_a_editar), columnas_cambiadas):
                            exito_total = False
                            
                if exito_total:
                    st.success("✅ ¡Base de datos de Ingresos actualizada correctamente!")
                    st.rerun()
                else:
                    st.error("❌ Hubo un detalle al intentar guardar algunos cambios.")
        else:
            st.info("💡 No hay registros de ingresos detectados en este ciclo.")   
           
           
           
                    
           
          
    # =========================================================================
    # 📉 PESTAÑA 2: REGISTRAR EGRESO
    # =========================================================================
    with tab2:
        st.subheader("📝 Formulario de Captura de Gastos / Egresos")
        
        conceptos_gastos = [
            "INSUMOS", "COSECHA", "SUELDOS", "CFE", 
            "RENTA MAQUINARIA", "MANTENIMIENTO", 
            "GASOLINA Y VIÁTICOS", "CONTABILIDAD", "ASESORÍA"
        ]
        concepto_seleccionado = st.selectbox("📉 Concepto del Gasto", conceptos_gastos, key="fin_egr_concepto_sel")
        
        ce1, ce2 = st.columns(2)
        with ce1:
            fecha_egreso = st.date_input("Fecha del Gasto", datetime.now(), key="fin_egr_fecha_input")
            folio_egreso = st.text_input("Folio Factura / Remisión", placeholder="Ej: F-12345 o 'SF'", key="fin_egr_folio_input")
            proveedor_egreso = st.text_input("Proveedor / Beneficiario", placeholder="¿A quién se le pagó?", key="fin_egr_prov_input")
            
        with ce2:
            moneda_egreso = st.selectbox("Tipo de Moneda", ["MXN", "USD"], key="fin_egr_moneda_sel")
            # HOMOLOGADO: Coincide perfectamente con los ingresos
            cuenta_origen = st.selectbox("Cuenta de Origen (Salida)", ["BBVA", "SANTANDER", "EFECTIVO"], key="fin_egr_cuenta_sel")
            ciclo_egreso = st.selectbox("Ciclo Productivo Imputable", ["Ciclo 2026", "Ciclo 2025"], key="fin_egr_ciclo_sel")
            
        ce3, ce4 = st.columns(2)
        with ce3:
            importe_egreso = st.number_input("Importe Total Neto del Gasto ($):", min_value=0.0, step=100.0, value=0.0, key="fin_egr_monto_input")
        with ce4:
            observaciones_egreso = st.text_area("Detalles o justificación del egreso", placeholder="Ej: Compra de fertilizantes...", height=110, key="fin_egr_obs_input")
            
        st.markdown("<br>", unsafe_allow_html=True)
        boton_guardar_egreso = st.button("💎 Registrar Egreso en Avalon", key="fin_egr_btn_guardar")
        
        if boton_guardar_egreso:
            if importe_egreso > 0:
                exito_eg = guardar_egreso(
                    categoria_egreso=concepto_seleccionado, 
                    fecha=fecha_egreso, 
                    folio=folio_egreso, 
                    proveedor_beneficiario=proveedor_egreso,
                    moneda=moneda_egreso, 
                    cuenta_origen=cuenta_origen, 
                    ciclo_productivo=ciclo_egreso, 
                    importe_total=importe_egreso, 
                    observaciones=observaciones_egreso
                )
                if exito_eg:
                    st.success(f"✅ ¡Gasto por ${importe_egreso:,.2f} registrado con éxito!")
                    st.rerun()
                else:
                    st.error("❌ Error al conectar con Postgres para guardar el egreso.")
            else:
                st.warning("⚠️ El importe del gasto debe ser mayor a $0.00.")
         
        # --- TABLA DE HISTORIAL DE EGRESOS EDITABLE ---
        st.markdown("---")
        st.subheader("📜 Historial de Egresos (Editable)")
        st.caption("💡 Haz doble clic en cualquier celda para modificar. Para borrar, selecciona la fila completa del lado izquierdo y presiona la tecla 'Supr' o 'Delete' en tu teclado, luego dale al botón Guardar Cambios.")
        
        df_egresos = obtener_ultimos_egresos("Ciclo 2026")
        
        if df_egresos is not None and not df_egresos.empty:
            egresos_editados = st.data_editor(
                df_egresos,
                num_rows="dynamic",
                disabled=["id"],
                column_config={
                    "importe_total": st.column_config.NumberColumn("Importe", format="$%,.2f"),
                    "fecha": st.column_config.DateColumn("Fecha"),
                },
                use_container_width=True,
                key="editor_egresos_key"
            )
            
            if st.button("💾 Guardar Cambios en Egresos", key="btn_save_egr"):
                cambios = st.session_state["editor_egresos_key"]
                exito_total = True
                
                # 1. Procesar filas eliminadas
                if cambios["deleted_rows"]:
                    for indice_fila in cambios["deleted_rows"]:
                        id_a_borrar = df_egresos.iloc[indice_fila]["id"]
                        if not eliminar_registro_db("egresos", int(id_a_borrar)):
                            exito_total = False
                
                # 2. Procesar filas modificadas
                if cambios["edited_rows"]:
                    for indice_fila, columnas_cambiadas in cambios["edited_rows"].items():
                        id_a_editar = df_egresos.iloc[int(indice_fila)]["id"]
                        if not actualizar_egreso_db(int(id_a_editar), columnas_cambiadas):
                            exito_total = False
                            
                if exito_total:
                    st.success("✅ ¡Base de datos de Egresos actualizada correctamente!")
                    st.rerun()
                else:
                    st.error("❌ Hubo un detalle al intentar guardar algunos cambios.")
        else:
            st.info("💡 No hay registros de egresos detectados en este ciclo.") 
         
         
    # =========================================================================
    # 📊 PESTAÑA 3: ANÁLISIS Y REPORTES
    # =========================================================================
