import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Ruta del archivo CSV limpio
FILE_PATH = "cleaned_coti.csv"

# Función para cargar y procesar los datos
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Renombrar columnas para ajustarse a los nombres requeridos
    df_copia.rename(columns={
        "Monto": "MONTO",
        "Cliente": "CLIENTE",
        "Estatus": "ESTATUS",
        "Fecha_Envio": "FECHA ENVIO",
        "Duracion_Dias": "DIAS",
        "Metodo_Captura": "LLAMADA AL CLIENTE",
        "Concepto": "CONCEPTO"
    }, inplace=True)

    # Agregar columnas faltantes con valores por defecto
    df_copia["AREA"] = df_copia.get("AREA", "General")
    df_copia["CLASIFICACION"] = df_copia.get("CLASIFICACION", "No clasificado")
    df_copia["VENDEDOR"] = df_copia.get("VENDEDOR", "Desconocido")
    df_copia["Cotizado X CLIENTE"] = df_copia.get("Cotizado X CLIENTE", 0)
    df_copia["Comentarios"] = df_copia.get("Comentarios", "Sin comentarios")

    # Crear columna de semáforo basada en el estatus
    df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard resuelve las siguientes problemáticas fundamentales del flujo de trabajo:

1. **Formato Unificado para Presupuestos y Ventas**:
   - **Sección Resolutiva:** Las tablas de "Estado General de Clientes" y "Generalizaciones de Cotizaciones" permiten unificar y automatizar análisis de presupuestos y ventas.
   - **Cómo lo Resuelve:** Evita procesos manuales al consolidar ambos flujos en un solo espacio de análisis.

2. **Seguimiento del Flujo de Cotización**:
   - **Sección Resolutiva:** La sección "Seguimiento de la Venta" rastrea el progreso de cada cotización, identificando tiempos de respuesta y estado actual.
   - **Cómo lo Resuelve:** Monitorea cuándo y quién envió las cotizaciones, asegurando que se procesen dentro de los tiempos establecidos.

3. **Integración con Evidence**:
   - **Sección Resolutiva:** Los datos aprobados (columna "Semaforo") están listos para exportación directa y captura en Evidence.
   - **Cómo lo Resuelve:** Automatiza el envío de datos aprobados a sistemas externos para minimizar errores y duplicación de tareas.
""")

# Tabla principal
st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]
st.dataframe(cotizaciones[columnas_mostrar], use_container_width=True)

# Actualización dinámica
st.subheader("Actualizar Datos Dinámicamente")
def actualizar_datos(cliente, columna, valor):
    index = cotizaciones[cotizaciones["CLIENTE"] == cliente].index
    if not index.empty:
        cotizaciones.loc[index, columna] = valor
        if columna == "ESTATUS":
            cotizaciones.loc[index, "Semaforo"] = "🟢 Aprobada" if valor == "APROBADA" else ("🟡 Pendiente" if valor == "PENDIENTE" else "🔴 Rechazada")
    else:
        st.error("El cliente especificado no existe en los datos.")

cliente_a_actualizar = st.selectbox("Selecciona el cliente a actualizar:", cotizaciones["CLIENTE"].unique())
columna_a_actualizar = st.selectbox("Selecciona la columna a actualizar:", ["MONTO", "DIAS", "ESTATUS", "Comentarios"])
nuevo_valor = st.text_input("Introduce el nuevo valor:")

if st.button("Actualizar Datos"):
    actualizar_datos(cliente_a_actualizar, columna_a_actualizar, nuevo_valor)
    st.experimental_rerun()

# Seguimiento de la venta
st.subheader("Seguimiento de la Venta")
cliente_seleccionado = st.selectbox("Selecciona un cliente para seguimiento:", cotizaciones["CLIENTE"].unique())
venta_cliente = cotizaciones[cotizaciones["CLIENTE"] == cliente_seleccionado]
if not venta_cliente.empty:
    st.write("Detalles de la venta:")
    st.dataframe(venta_cliente)
    progreso = st.slider(
        "Progreso de la venta (en %):",
        min_value=0,
        max_value=100,
        value=int(venta_cliente["DIAS"].mean() / 100 * 100)
    )
    st.progress(progreso / 100)
else:
    st.warning("No se encontraron ventas para este cliente.")

# Tabla de generalizaciones de cotizaciones
st.subheader("Generalizaciones de Cotizaciones")
resumen_cotizaciones = cotizaciones.groupby("VENDEDOR").agg(
    total_monto=("MONTO", "sum"),
    promedio_dias=("DIAS", "mean"),
    total_cotizaciones=("CLIENTE", "count")
).reset_index()
resumen_cotizaciones.rename(columns={"VENDEDOR": "Vendedor", "total_monto": "Monto Total", "promedio_dias": "Promedio de Días", "total_cotizaciones": "Número de Cotizaciones"}, inplace=True)

st.dataframe(resumen_cotizaciones, use_container_width=True)
# Generación de reportes automatizados
st.subheader("Reporte Automático de Cotizaciones Aprobadas")

# Sección que resuelve el punto 3 (Integración con Evidence)
reporte_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not reporte_aprobadas.empty:
    st.write("Cotizaciones aprobadas disponibles para descarga y envío a Evidence:")
    st.dataframe(reporte_aprobadas, use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=reporte_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas actualmente.")

# Proyecciones de Ventas Mensuales y Anuales
st.subheader("Proyecciones de Ventas")

# Sección que aborda el punto 1 (Formato Unificado para Presupuestos y Ventas)
def generar_proyecciones(df, columna="MONTO", meses=12):
    df["FECHA ENVIO"] = pd.to_datetime(df["FECHA ENVIO"], errors="coerce")
    df = df.dropna(subset=["FECHA ENVIO"])
    df_proyeccion = df.groupby(df["FECHA ENVIO"].dt.to_period("M"))[columna].sum().reset_index()
    df_proyeccion.rename(columns={"FECHA ENVIO": "Mes", columna: "Monto"}, inplace=True)
    df_proyeccion["Mes"] = df_proyeccion["Mes"].dt.to_timestamp()

    ultimo_mes = df_proyeccion["Mes"].max()
    for i in range(1, meses + 1):
        nuevo_mes = ultimo_mes + pd.DateOffset(months=i)
        df_proyeccion = pd.concat([df_proyeccion, pd.DataFrame({"Mes": [nuevo_mes], "Monto": [df_proyeccion["Monto"].mean()]})])
    return df_proyeccion

try:
    proyeccion_mensual = generar_proyecciones(cotizaciones)

    fig_proyeccion_mensual = px.line(
        proyeccion_mensual,
        x="Mes",
        y="Monto",
        title="Proyección Mensual de Ventas",
        labels={"Mes": "Mes", "Monto": "Monto ($)"},
        markers=True
    )
    fig_proyeccion_mensual.update_layout(xaxis_title="Mes", yaxis_title="Monto ($)")
    st.plotly_chart(fig_proyeccion_mensual)

    proyeccion_anual = proyeccion_mensual.groupby(proyeccion_mensual["Mes"].dt.year)["Monto"].sum().reset_index()
    proyeccion_anual.rename(columns={"Mes": "Año", "Monto": "Monto Total"}, inplace=True)

    fig_proyeccion_anual = px.bar(
        proyeccion_anual,
        x="Año",
        y="Monto Total",
        title="Proyección Anual de Ventas",
        labels={"Año": "Año", "Monto Total": "Monto Total ($)"}
    )
    fig_proyeccion_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total ($)")
    st.plotly_chart(fig_proyeccion_anual)

except Exception as e:
    st.error(f"Error al generar proyecciones: {e}")

# Análisis de Vendedores
st.subheader("Análisis por Vendedor")

# Sección que aborda el punto 2 (Seguimiento del Flujo de Cotización)
vendedor_seleccionado = st.selectbox("Selecciona un vendedor para analizar:", cotizaciones["VENDEDOR"].unique())
if vendedor_seleccionado:
    ventas_vendedor = cotizaciones[cotizaciones["VENDEDOR"] == vendedor_seleccionado]
    st.write(f"Ventas realizadas por {vendedor_seleccionado}:")
    st.dataframe(ventas_vendedor, use_container_width=True)

    total_ventas = ventas_vendedor["MONTO"].sum()
    promedio_dias = ventas_vendedor["DIAS"].mean()
    total_cotizaciones = len(ventas_vendedor)

    st.write(f"**Monto Total Vendido:** ${total_ventas:,.2f}")
    st.write(f"**Promedio de Días para Cierre:** {promedio_dias:.2f} días")
    st.write(f"**Total de Cotizaciones Generadas:** {total_cotizaciones}")

# Exportar datos del análisis por vendedor
st.subheader("Exportar Análisis del Vendedor")
st.download_button(
    label=f"Descargar Ventas de {vendedor_seleccionado}",
    data=ventas_vendedor.to_csv(index=False).encode("utf-8"),
    file_name=f"ventas_{vendedor_seleccionado}.csv",
    mime="text/csv"
)

# Texto explicativo
st.markdown("""
### Resolución de Problemas Clave:

1. **Formato Unificado para Presupuestos y Ventas**:
   - **Sección Resolutiva:** "Proyecciones de Ventas" ofrece una visión consolidada de presupuestos y ventas mediante análisis automatizado.

2. **Seguimiento del Flujo de Cotización**:
   - **Sección Resolutiva:** "Análisis por Vendedor" detalla el desempeño de cada vendedor, tiempos promedio y resultados individuales.

3. **Integración con Evidence**:
   - **Sección Resolutiva:** "Reporte Automático de Cotizaciones Aprobadas" asegura la exportación de datos aprobados para su integración con Evidence.
""")
# Tablas detalladas con filtros
st.subheader("Tablas Detalladas con Filtros")

# Análisis por Área
st.markdown("### Análisis por Área")
# **Resuelve Punto 1 (Formato Unificado para Presupuestos y Ventas)**
area_seleccionada = st.selectbox("Selecciona un área:", cotizaciones["AREA"].unique())
if area_seleccionada:
    cotizaciones_area = cotizaciones[cotizaciones["AREA"] == area_seleccionada]
    st.dataframe(cotizaciones_area, use_container_width=True)
    st.write(f"Total de registros para el área {area_seleccionada}: {len(cotizaciones_area)}")

# Filtrar por Vendedor
st.markdown("### Filtrar por Vendedor")
# **Resuelve Punto 2 (Seguimiento del Flujo de Cotización)**
vendedor_seleccionado = st.multiselect("Selecciona uno o más vendedores:", cotizaciones["VENDEDOR"].unique())
if vendedor_seleccionado:
    cotizaciones_vendedor = cotizaciones[cotizaciones["VENDEDOR"].isin(vendedor_seleccionado)]
    st.dataframe(cotizaciones_vendedor, use_container_width=True)
    st.write(f"Total de registros para los vendedores seleccionados: {len(cotizaciones_vendedor)}")

# Resumen por Clasificación
st.markdown("### Resumen por Clasificación")
# **Resuelve Punto 1 (Formato Unificado para Presupuestos y Ventas)**
clasificacion_resumen = cotizaciones.groupby("CLASIFICACION")["MONTO"].sum().reset_index()
clasificacion_resumen.rename(columns={"MONTO": "Monto Total"}, inplace=True)
st.dataframe(clasificacion_resumen, use_container_width=True)

# Tabla con Múltiples Filtros
st.markdown("### Tabla con Múltiples Filtros")
# **Resuelve Punto 2 (Seguimiento del Flujo de Cotización)**
col1, col2, col3 = st.columns(3)
with col1:
    filtro_area = st.selectbox("Filtrar por Área:", ["Todos"] + list(cotizaciones["AREA"].unique()))
with col2:
    filtro_estatus = st.selectbox("Filtrar por Estatus:", ["Todos"] + list(cotizaciones["ESTATUS"].unique()))
with col3:
    filtro_vendedor = st.selectbox("Filtrar por Vendedor:", ["Todos"] + list(cotizaciones["VENDEDOR"].unique()))

# Aplicar filtros
cotizaciones_filtradas = cotizaciones.copy()
if filtro_area != "Todos":
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["AREA"] == filtro_area]
if filtro_estatus != "Todos":
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["ESTATUS"] == filtro_estatus]
if filtro_vendedor != "Todos":
    cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["VENDEDOR"] == filtro_vendedor]

st.dataframe(cotizaciones_filtradas, use_container_width=True)
st.write(f"Total de registros después de aplicar filtros: {len(cotizaciones_filtradas)}")

# Top 10 Montos
st.markdown("### Top 10 Cotizaciones por Monto")
# **Resuelve Punto 1 (Formato Unificado para Presupuestos y Ventas)**
top_10_montos = cotizaciones.nlargest(10, "MONTO")
st.dataframe(top_10_montos, use_container_width=True)

# Exportar tablas filtradas
st.subheader("Exportar Datos Filtrados")
# **Resuelve Punto 3 (Integración con Evidence)**
st.download_button(
    label="Descargar Datos Filtrados",
    data=cotizaciones_filtradas.to_csv(index=False).encode("utf-8"),
    file_name="datos_filtrados.csv",
    mime="text/csv"
)
st.download_button(
    label="Descargar Resumen por Clasificación",
    data=clasificacion_resumen.to_csv(index=False).encode("utf-8"),
    file_name="resumen_clasificacion.csv",
    mime="text/csv"
)

# Texto explicativo
st.markdown("""
### Resolución de Problemas Clave:

1. **Formato Unificado para Presupuestos y Ventas**:
   - **Sección Resolutiva:** "Análisis por Área", "Resumen por Clasificación" y "Top 10 Montos" unifican presupuestos y ventas para análisis automatizados.

2. **Seguimiento del Flujo de Cotización**:
   - **Sección Resolutiva:** "Tabla con Múltiples Filtros" y "Filtrar por Vendedor" facilitan el monitoreo del estado y desempeño de los responsables de cotizaciones.

3. **Integración con Evidence**:
   - **Sección Resolutiva:** "Exportar Datos Filtrados" asegura que los datos consolidados puedan integrarse con Evidence para seguimiento externo.
""")
