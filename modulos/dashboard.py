import streamlit as st
import datetime
from database import consultar_proveedores  # Mantenemos tu import real

def mostrar_dashboard():
    
    
    st.markdown("""
    <style>
        /* Reduce el espacio muerto superior del contenedor principal */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
    </style>
""", unsafe_allow_html=True)
    
    
    
    st.title("📊 Panel de Control")
    st.markdown("Gestión de ciclos, saldos y estimación de utilidad para **Nogalera Los Mezquites**")
    st.markdown("---")
    
    # =========================================================
    # BLOQUE 1: PALANCAS Y FILTROS (Entradas del usuario)
    # =========================================================
    st.subheader("⚙️ Parámetros del Ciclo Operativo")
    
    col_fecha, col_kilos, col_precio = st.columns(3)
    
    with col_fecha:
        # Filtro de periodo (Por defecto el año en curso)
        hoy = datetime.date.today()
        fecha_inicio = datetime.date(hoy.year, 1, 1)
        fecha_fin = datetime.date(hoy.year, 12, 31)
        
        periodo = st.date_input(
            "Periodo del Ciclo:",
            value=(fecha_inicio, fecha_fin),
            format="DD/MM/YYYY"
        )
        
    with col_kilos:
        # Estimación de cosecha en kg
        kilos_esperados = st.number_input(
            "Cosecha Estimada (Kg):", 
            min_value=0, 
            value=15000, 
            step=1000
        )
        
    with col_precio:
        # Precio esperado por kilo
        precio_esperado = st.number_input(
            "Precio Esperado por Kg (MXN):", 
            min_value=0.0, 
            value=85.0, 
            step=5.0
        )

    # =========================================================
    # LÓGICA MATEMÁTICA (Simulación con datos temporales)
    # =========================================================
    # 1. Ingreso Bruto Estimado
    ingreso_estimado = kilos_esperados * precio_esperado
    
    # 2. Datos simulados de gastos reales extraídos de tus 10 conceptos
    # (En el siguiente paso los jalaremos con queries SUM(monto) WHERE concepto = 'X')
    gastos_reales_totales = 45000.00  # Ejemplo: lo que ya se pagó en el periodo
    gastos_estimados_restantes = 120000.00  # Ejemplo: lo presupuestado para el resto del ciclo
    
    egreso_proyectado_total = gastos_reales_totales + gastos_estimados_restantes
    utilidad_proyectada = ingreso_estimado - egreso_proyectado_total
    
    # 3. Saldos actuales (Efectivo + Bancos)
    saldo_bancos = 85400.00   # Simulación temporal
    saldo_efectivo = 12500.00 # Simulación temporal
    liquidez_total = saldo_bancos + saldo_efectivo

    # =========================================================
    # BLOQUE 2: TARJETAS DE PROYECCIÓN Y LIQUIDEZ
    # =========================================================
    
    # =========================================================
    # BLOQUE 2: TARJETAS DE PROYECCIÓN Y LIQUIDEZ
    # =========================================================
    st.markdown("---")
    st.subheader("📈 Proyección Financiera del Ciclo")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            label="💰 Ingreso Bruto Estimado", 
            value=f"${ingreso_estimado:,.0f}"
        )
    with c2:
        st.metric(
            label="📉 Egreso Proyectado Total", 
            value=f"${egreso_proyectado_total:,.0f}", 
            delta=f"Real: ${gastos_reales_totales:,.0f}", 
            delta_color="inverse"
        )
    with c3:
        # Color verde si hay ganancia, rojo si no
        color_utilidad = "🟢" if utilidad_proyectada >= 0 else "🔴"
        st.metric(
            label=f"{color_utilidad} Utilidad Neta Proyectada", 
            value=f"${utilidad_proyectada:,.2f}"
        )

    # Fila de Saldos Actuales
    st.markdown("### 🏦 Disponibilidad de Efectivo (Liquidez)")
    sb1, sb2, sb3 = st.columns(3)
    with sb1:
        st.caption(f"**Bancos:** ${saldo_bancos:,.2f}")
    with sb2:
        st.caption(f"**Efectivo / Caja:** ${saldo_efectivo:,.2f}")
    with sb3:
        st.markdown(f"**Disponible Total:** `${liquidez_total:,.2f}`")
    

    # =========================================================
    # BLOQUE 3: EL DESGLOSE DE LOS 10 CONCEPTOS
    # =========================================================
    st.markdown("---")
    st.subheader("📋 Desglose de Egresos por Concepto")
    st.markdown("Monitoreo de tus 10 conceptos clave frente al estimado del ciclo:")

    # Lista de tus conceptos oficiales
    conceptos = [
        "CFE", "GASOLINA", "VIÁTICOS", "MANTENIMIENTO", "INSUMOS", 
        "SUELDOS", "RENTA MAQUINARIA", "COSECHA", "CONTABILIDAD", "ASESORÍA"
    ]
    
    # Generamos la tabla visual para cada concepto
    for con in conceptos:
        # Columnas para simular el avance de cada gasto
        col_name, col_progreso, col_num = st.columns([2, 3, 2])
        
        with col_name:
            st.markdown(f"**{con}**")
            
        with col_progreso:
            # Barra de progreso visual (Simulada al 30% de uso para el ejemplo)
            st.progress(0.30)
            
        with col_num:
            st.caption("Real: `$3,000` | Restante: `$7,000`")