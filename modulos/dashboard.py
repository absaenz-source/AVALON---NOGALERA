import streamlit as st
import pandas as pd
from database import obtener_totales_por_cuenta, obtener_gastos_por_categoria

def mostrar_dashboard():
    # Reducción de espacios superiores para estética en el tablero principal
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Resumen Ejecutivo del Ciclo Activo")
    st.write("Cifras consolidadas en tiempo real basadas en tus registros de Postgres.")
    st.markdown("---")
    
    # 1. TRAER DATOS REALES DE LA BASE DE DATOS (Fijo a Ciclo 2026 temporalmente)
    # Nota: Aquí es donde resolveremos el desfase de sumatorias analizando qué devuelve Postgres
    flujo_cuentas = obtener_totales_por_cuenta("Ciclo 2026")
    gastos_reales = obtener_gastos_por_categoria("Ciclo 2026")
    
    # Sumatorias globales directas de Postgres
    total_ingresos_real = flujo_cuentas.get("total_ingresos_global", 0.0)
    total_egresado_real = flujo_cuentas.get("total_egresos_global", 0.0)
    saldo_calculado_real = total_ingresos_real - total_egresado_real

    # Extraer flujos específicos para el desglose de cuentas de manera segura
    ingresos_bbva = flujo_cuentas.get("BBVA", {}).get("ingresos", 0.0)
    egresos_bbva = flujo_cuentas.get("BBVA", {}).get("egresos", 0.0)
    ingresos_efectivo = flujo_cuentas.get("Efectivo", {}).get("ingresos", 0.0)
    egresos_efectivo = flujo_cuentas.get("Efectivo", {}).get("egresos", 0.0)
    
    # 2. SECCIÓN DE GRANDES TOTALES
    st.markdown("### 📈 Balance Consolidado del Ciclo")
    col_tot_ing, col_tot_egr, col_tot_sal = st.columns(3)
    
    with col_tot_ing:
        st.metric(label="🟢 TOTAL INGRESOS REGISTRADOS", value=f"${total_ingresos_real:,.2f}")
    with col_tot_egr:
        st.metric(label="🔴 TOTAL EGRESOS REALES", value=f"${total_egresado_real:,.2f}")
    with col_tot_sal:
        st.metric(label="💰 SALDO NETO EN SISTEMA", value=f"${saldo_calculado_real:,.2f}")
        
    st.markdown("---")
    
    # Variables de proyección (Cuentas por pagar y estimaciones de Nuez)
    cuentas_por_pagar = 62400.00
    volumen_estimado = 12000.00  
    precio_esperado = 90.00      
    valor_produccion = volumen_estimado * precio_esperado
    
    # 3. COLUMNAS DE DESGLOSE INTERNO
    col_saldos, col_gastos, col_produccion = st.columns([1.2, 1.1, 1.2])
    
    with col_saldos:
        st.markdown("### 🏦 Flujo por Cuentas")
        saldo_bbva = ingresos_bbva - egresos_bbva
        st.metric(label="💳 BBVA (Saldo Real)", value=f"${saldo_bbva:,.2f}")
        
        saldo_efectivo = ingresos_efectivo - egresos_efectivo
        st.metric(label="💵 Efectivo (Saldo Real)", value=f"${saldo_efectivo:,.2f}")
        
        # Cuenta de respaldo Santander u otras
        ingresos_otras = flujo_cuentas.get("Otras", {}).get("ingresos", 0.0)
        egresos_otras = flujo_cuentas.get("Otras", {}).get("egresos", 0.0)
        saldo_otras = ingresos_otras - egresos_otras
        
        if saldo_otras != 0:
            st.metric(label="🏦 Otras Cuentas / No Clasificado", value=f"${saldo_otras:,.2f}", help="Registros con nombres antiguos o de otras instituciones")
        
        st.markdown("---")
        st.metric(label="⚠️ Cuentas por Pagar", value=f"${cuentas_por_pagar:,.2f}", delta=f"-${cuentas_por_pagar:,.2f}", delta_color="inverse")
        
        balance_final = saldo_calculado_real - cuentas_por_pagar
        st.subheader(f"⚖️ Balance Final: ${balance_final:,.2f}")
    
    with col_gastos:
        st.markdown("### 📉 Detalle por Categoría")
        st.write("Desglose acumulado:")
        
        if gastos_reales:
            for g_concepto, g_importe in gastos_reales.items():
                st.markdown(f"**{g_concepto}:** ${g_importe:,.2f}")
        else:
            st.info("No hay egresos registrados en este ciclo todavía.")

    with col_produccion:
        st.markdown("### 🚜 Proyecciones de Producción")
        st.metric(label="📦 Volumen Esperado", value=f"{volumen_estimado:,.0f} Kg")
        st.metric(label="🏷️ Precio Esperado / Kg", value=f"${precio_esperado:,.2f}")
        st.metric(label="💎 Valor de Cosecha", value=f"${valor_produccion:,.2f}", delta=f"+${valor_produccion:,.2f}")
        
        st.markdown("---")
        st.markdown("### 🏁 Proyección Final")
        saldo_final_proyectado = saldo_calculado_real + valor_produccion
        
        st.metric(
            label="🚀 SALDO FINAL ESTIMADO", 
            value=f"${saldo_final_proyectado:,.2f}",
            delta=f"${saldo_final_proyectado - saldo_calculado_real:,.2f} vs Actual"
        )