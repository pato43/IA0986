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
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

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

    # Simular datos faltantes para asegurar compatibilidad
    if "AREA" not in df_copia.columns:
        df_copia["AREA"] = "General"
    if "CLASIFICACION" not in df_copia.columns:
        df_copia["CLASIFICACION"] = "No clasificado"
    if "VENDEDOR" not in df_copia.columns:
        df_copia["VENDEDOR"] = "Desconocido"
    if "Semaforo" not in df_copia.columns:
        df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
            lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
        )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Verificar si el DataFrame está vacío
if cotizaciones.empty:
    st.stop()

# Crear una copia para simulación y edición
cotizaciones_simuladas = cotizaciones.copy()

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard resuelve las siguientes problemáticas principales:

1. **Formato Unificado para Presupuestos y Ventas**:
   - **Sección Resolutiva:** Tablas interactivas en "Estado General de Clientes".
   - **Cómo lo Resuelve:** Consolida presupuestos y ventas en un solo análisis dinámico.

2. **Seguimiento del Flujo de Cotización**:
   - **Sección Resolutiva:** "Seguimiento de la Venta" identifica clientes, responsables y tiempos.
   - **Cómo lo Resuelve:** Agrega filtros para rastrear estados y responsables, monitoreando plazos críticos.

3. **Integración con Evidence**:
   - **Sección Resolutiva:** Tablas filtradas por "Semaforo" listas para exportación.
   - **Cómo lo Resuelve:** Automatiza la transferencia de datos aprobados para minimizar errores.
""")

# Tabla principal con filtros dinámicos
st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]

# Validar columnas disponibles
columnas_disponibles = [col for col in columnas_mostrar if col in cotizaciones_simuladas.columns]

# Crear opciones dinámicas de filtrado
filtros = {}
if st.checkbox("Filtrar por Área"):
    filtros['AREA'] = st.multiselect("Selecciona Área(s):", options=cotizaciones_simuladas['AREA'].dropna().unique())
if st.checkbox("Filtrar por Estatus"):
    filtros['ESTATUS'] = st.multiselect("Selecciona Estatus(es):", options=cotizaciones_simuladas['ESTATUS'].dropna().unique())
if st.checkbox("Filtrar por Vendedor"):
    filtros['VENDEDOR'] = st.multiselect("Selecciona Vendedor(es):", options=cotizaciones_simuladas['VENDEDOR'].dropna().unique())

# Aplicar los filtros dinámicamente
cotizaciones_filtradas = cotizaciones_simuladas.copy()
for columna, valores in filtros.items():
    if valores:
        cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas[columna].isin(valores)]

st.dataframe(cotizaciones_filtradas[columnas_disponibles], use_container_width=True)

# Visualización de métricas generales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones_filtradas))
col2.metric("Monto Total", f"${cotizaciones_filtradas['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones_filtradas['DIAS'].mean():.2f}")

# Seguimiento de la Venta (Punto 2)
st.subheader("Seguimiento de la Venta")
cliente_seleccionado = st.selectbox("Selecciona un cliente para seguimiento:", cotizaciones_simuladas["CLIENTE"].unique())
venta_cliente = cotizaciones_simuladas[cotizaciones_simuladas["CLIENTE"] == cliente_seleccionado]
if not venta_cliente.empty:
    st.write("Detalles de la venta:")
    st.dataframe(venta_cliente, use_container_width=True)
    progreso = st.slider(
        "Progreso de la venta (en %):",
        min_value=0,
        max_value=100,
        value=int((venta_cliente["DIAS"].iloc[0] / 30) * 100)
    )
    st.progress(progreso / 100)

# Gráfico de Proyección Mensual (Punto 1)
st.subheader("Proyección de Ventas del Próximo Mes")
proyeccion_mensual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:7])["MONTO"].sum().reset_index()
proyeccion_mensual.columns = ["Mes", "Monto"]
fig_proyeccion_mensual = px.line(
    proyeccion_mensual,
    x="Mes",
    y="Monto",
    title="Proyección Mensual de Ventas",
    labels={"Mes": "Mes", "Monto": "Monto ($)"},
    markers=True
)
st.plotly_chart(fig_proyeccion_mensual)

# Gráfico de Proyección Anual (Punto 1)
st.subheader("Proyección de Ventas Anual")
proyeccion_anual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:4])["MONTO"].sum().reset_index()
proyeccion_anual.columns = ["Año", "Monto"]
fig_proyeccion_anual = px.line(
    proyeccion_anual,
    x="Año",
    y="Monto",
    title="Proyección Anual de Ventas",
    labels={"Año": "Año", "Monto": "Monto ($)"},
    markers=True
)
st.plotly_chart(fig_proyeccion_anual)
# Generación de reportes automatizados
st.subheader("Reporte Automático de Cotizaciones Aprobadas")

# **Resuelve Punto 3: Integración con Evidence**
reporte_aprobadas = cotizaciones_simuladas[cotizaciones_simuladas["Semaforo"] == "🟢 Aprobada"]
if not reporte_aprobadas.empty:
    st.write("Cotizaciones aprobadas disponibles para descarga y envío a Evidence:")
    st.dataframe(reporte_aprobadas, use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=reporte_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
    st.markdown("""**Cómo se Resuelve:** Esta sección permite generar y exportar automáticamente las cotizaciones aprobadas para integrarlas en Evidence.
Minimiza errores al automatizar la transferencia de datos aprobados.""")
else:
    st.info("No hay cotizaciones aprobadas actualmente.")

# Proyecciones de Ventas Mensuales y Anuales
st.subheader("Proyecciones de Ventas")

# **Resuelve Punto 1: Formato Unificado para Presupuestos y Ventas**
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
    proyeccion_mensual = generar_proyecciones(cotizaciones_simuladas)

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

    fig_proyeccion_anual = px.line(
        proyeccion_anual,
        x="Año",
        y="Monto Total",
        title="Proyección Anual de Ventas",
        labels={"Año": "Año", "Monto Total": "Monto Total ($)"},
        markers=True
    )
    fig_proyeccion_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total ($)")
    st.plotly_chart(fig_proyeccion_anual)

    st.markdown("""**Cómo se Resuelve:** Esta sección consolida presupuestos y ventas en un único análisis dinámico.
Permite proyectar ventas futuras de manera mensual y anual, optimizando la planeación financiera.""")

except Exception as e:
    st.error(f"Error al generar proyecciones: {e}")

# Análisis de Vendedores
st.subheader("Análisis por Vendedor")

# **Resuelve Punto 2: Seguimiento del Flujo de Cotización**
vendedor_seleccionado = st.selectbox("Selecciona un vendedor para analizar:", cotizaciones_simuladas["VENDEDOR"].unique())
if vendedor_seleccionado:
    ventas_vendedor = cotizaciones_simuladas[cotizaciones_simuladas["VENDEDOR"] == vendedor_seleccionado]
    st.write(f"Ventas realizadas por {vendedor_seleccionado}:")
    st.dataframe(ventas_vendedor, use_container_width=True)

    total_ventas = ventas_vendedor["MONTO"].sum()
    promedio_dias = ventas_vendedor["DIAS"].mean()
    total_cotizaciones = len(ventas_vendedor)

    st.write(f"**Monto Total Vendido:** ${total_ventas:,.2f}")
    st.write(f"**Promedio de Días para Cierre:** {promedio_dias:.2f} días")
    st.write(f"**Total de Cotizaciones Generadas:** {total_cotizaciones}")

    # Filtro adicional por concepto
    concepto_vendedor = st.multiselect(
        "Filtrar por concepto:",
        ventas_vendedor["CONCEPTO"].unique()
    )
    if concepto_vendedor:
        ventas_vendedor_filtradas = ventas_vendedor[ventas_vendedor["CONCEPTO"].isin(concepto_vendedor)]
        st.dataframe(ventas_vendedor_filtradas, use_container_width=True)

    st.markdown("""**Cómo se Resuelve:** Este análisis identifica a los responsables y monitorea su desempeño.
Facilita el seguimiento del flujo de cotización, evaluando tiempos y montos asociados a cada vendedor.""")

# Exportar datos del análisis por vendedor
st.subheader("Exportar Análisis del Vendedor")
st.download_button(
    label=f"Descargar Ventas de {vendedor_seleccionado}",
    data=ventas_vendedor.to_csv(index=False).encode("utf-8"),
    file_name=f"ventas_{vendedor_seleccionado}.csv",
    mime="text/csv"
)
# Parte 3: Exportación e integración con Evidence y seguimiento detallado

# Seguimiento detallado de las ventas
st.subheader("Seguimiento Detallado de la Venta")
st.markdown("""
**Punto 2: Mandan la cotización y esperan que (le demos salida)**  
En esta sección, se realiza un seguimiento dinámico de las cotizaciones enviadas, el cliente asociado, el responsable, y los tiempos involucrados.
""")

# Tabla dinámica con seguimiento de cotizaciones
seguimiento_columnas = ["CLIENTE", "CONCEPTO", "VENDEDOR", "FECHA ENVIO", "DIAS", "ESTATUS", "Semaforo"]
st.dataframe(cotizaciones_filtradas[seguimiento_columnas], use_container_width=True)

# Exportación de datos para Evidence
st.subheader("Exportación de Datos para Evidence")
st.markdown("""
**Punto 3: Ya salió la cotización**  
Aquí puedes exportar las cotizaciones aprobadas a formatos compatibles para su integración con Evidence.
""")

cotizaciones_aprobadas = cotizaciones_filtradas[cotizaciones_filtradas["Semaforo"] == "🟢 Aprobada"]
if not cotizaciones_aprobadas.empty:
    st.dataframe(cotizaciones_aprobadas, use_container_width=True)

    # Exportar a JSON
    st.download_button(
        label="Descargar JSON de Cotizaciones Aprobadas",
        data=cotizaciones_aprobadas.to_json(orient="records", indent=4).encode("utf-8"),
        file_name="cotizaciones_aprobadas.json",
        mime="application/json"
    )

    # Exportar a CSV
    st.download_button(
        label="Descargar CSV de Cotizaciones Aprobadas",
        data=cotizaciones_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas disponibles para exportar.")

# Generar reporte automatizado
st.subheader("Generación de Reportes")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Genera un reporte consolidado que incluye tanto presupuestos como ventas.
""")
if st.button("Generar Reporte"):
    try:
        # Simular creación de un archivo consolidado
        reporte_consolidado = cotizaciones_filtradas.groupby(["AREA", "VENDEDOR"]).agg({
            "MONTO": "sum",
            "DIAS": "mean"
        }).reset_index()
        reporte_consolidado.columns = ["Área", "Vendedor", "Monto Total", "Promedio Días"]
        st.dataframe(reporte_consolidado, use_container_width=True)
    except Exception as e:
        st.error(f"Error al generar el reporte: {e}")

# Envío de reportes por correo (simulado)
st.subheader("Envío de Reportes por Correo")
st.markdown("""
**Facilita la distribución de reportes automatizados**  
En esta sección puedes enviar por correo los reportes generados.
""")
correo = st.text_input("Ingresa el correo electrónico:")
if st.button("Enviar Reporte"):
    if correo:
        st.success(f"Reporte enviado exitosamente a {correo} (simulado).")
    else:
        st.error("Por favor, ingresa un correo válido.")
