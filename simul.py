import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("Dashboard de Cotizaciones")

# Cargar y procesar datos
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    # Copiar el dataframe y simular datos faltantes
    df_copia = df.copy()

    # Limpieza y simulación de datos faltantes
    df_copia["Monto"] = pd.to_numeric(df_copia["Monto"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(100000)
    df_copia["Avance_Porcentaje"] = pd.to_numeric(df_copia["Avance_Porcentaje"], errors="coerce").fillna(50)
    df_copia["2020"] = pd.to_numeric(df_copia["2020"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(2000000)
    df_copia["2021"] = pd.to_numeric(df_copia["2021"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(3000000)
    df_copia["Estatus"] = df_copia["Estatus"].fillna("Desconocido")

    # Agregar semáforo
    df_copia["Semaforo"] = df_copia["Avance_Porcentaje"].apply(lambda x: "🟢 Aprobada" if x >= 75 else ("🟡 Pendiente" if x >= 50 else "🔴 Rechazada"))
    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Layout inicial con pestañas
menu = st.tabs(["Resumen General", "Tablas Detalladas", "Edición de Datos"])

# Pestaña: Resumen General
with menu[0]:
    st.header("Resumen General de Cotizaciones")

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cotizaciones", len(cotizaciones))
    col2.metric("Monto Total", f"${cotizaciones['Monto'].sum():,.2f}")
    col3.metric("Promedio de Avance", f"{cotizaciones['Avance_Porcentaje'].mean():.2f}%")

    # Gráfico de barras de ventas por año
    st.subheader("Monto Anual de Ventas")
    ventas_anuales = cotizaciones[["2020", "2021"]].sum().reset_index()
    ventas_anuales.columns = ["Año", "Monto"]

    fig_ventas = px.bar(
        ventas_anuales,
        x="Año",
        y="Monto",
        text="Monto",
        title="Monto Total de Ventas por Año",
        labels={"Monto": "Monto Total", "Año": "Año"},
        color="Año",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_ventas.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_ventas.update_layout(xaxis_title="Año", yaxis_title="Monto Total")
    st.plotly_chart(fig_ventas)

# Pestaña: Tablas Detalladas
with menu[1]:
    st.header("Tablas Detalladas")

    # Resumen por cliente
    st.subheader("Resumen por Cliente")
    tabla_cliente = cotizaciones.groupby("Cliente").agg(
        Total_Monto=("Monto", "sum"),
        Total_Cotizaciones=("Cliente", "count"),
        Promedio_Avance=("Avance_Porcentaje", "mean"),
        Semaforo=("Semaforo", "first")
    ).reset_index()
    st.dataframe(tabla_cliente, use_container_width=True)

    # Resumen por área
    st.subheader("Resumen por Área")
    tabla_area = cotizaciones.groupby("Area").agg(
        Total_Monto=("Monto", "sum"),
        Total_Cotizaciones=("Area", "count"),
        Promedio_Avance=("Avance_Porcentaje", "mean"),
        Semaforo=("Semaforo", "first")
    ).reset_index()
    st.dataframe(tabla_area, use_container_width=True)

# Pestaña: Edición de Datos
with menu[2]:
    st.header("Edición de Datos")

    # Selección de filtros
    cliente_filtrado = st.selectbox("Selecciona un cliente para filtrar:", ["Todos"] + cotizaciones["Cliente"].unique().tolist())
    area_filtrada = st.selectbox("Selecciona un área para filtrar:", ["Todos"] + cotizaciones["Area"].unique().tolist())

    datos_filtrados = cotizaciones.copy()
    if cliente_filtrado != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Cliente"] == cliente_filtrado]
    if area_filtrada != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Area"] == area_filtrada]

    st.dataframe(datos_filtrados, use_container_width=True)

    # Edición interactiva
    columna_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Avance_Porcentaje"])
    nuevo_valor = st.text_input("Nuevo valor para la columna seleccionada")
    if st.button("Aplicar Cambios"):
        datos_filtrados[columna_editar] = nuevo_valor
        st.success("Cambios aplicados correctamente.")
# Continuación del dashboard: Parte 2
st.header("Análisis Detallado y Pronósticos")

# Análisis por Vendedor
st.subheader("Desempeño por Vendedor")

tabla_vendedores = cotizaciones.groupby("Vendedor").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Semaforo=("Semaforo", "first")
).reset_index()

st.dataframe(tabla_vendedores, use_container_width=True)

fig_vendedores = px.bar(
    tabla_vendedores,
    x="Vendedor",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Vendedor",
    labels={"Total_Monto": "Monto Total", "Vendedor": "Vendedor", "Promedio_Avance": "Avance Promedio"},
    text="Total_Cotizaciones",
    color_continuous_scale="Bluered"
)
fig_vendedores.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_vendedores.update_layout(xaxis_title="Vendedor", yaxis_title="Monto Total", xaxis_tickangle=-45)
st.plotly_chart(fig_vendedores)

# Pronóstico de Ventas por Mes
st.subheader("Pronóstico de Ventas por Mes")

# Simular datos mensuales si no existen
if "Pronostico_Suavizado" not in cotizaciones.columns:
    cotizaciones["Pronostico_Suavizado"] = pd.Series([50000 + i * 1000 for i in range(len(cotizaciones))])

ventas_mensuales = cotizaciones.groupby(cotizaciones.index // 10).agg(
    Pronostico_Suavizado=("Pronostico_Suavizado", "sum")
).reset_index()
ventas_mensuales.columns = ["Mes", "Monto"]

fig_pronostico = px.line(
    ventas_mensuales,
    x="Mes",
    y="Monto",
    title="Pronóstico Mensual de Ventas",
    labels={"Monto": "Monto Total Pronosticado", "Mes": "Mes"},
    markers=True
)
fig_pronostico.update_layout(xaxis_title="Mes", yaxis_title="Monto Total")
st.plotly_chart(fig_pronostico)

# Resumen por Clasificación
st.subheader("Desempeño por Clasificación de Clientes")

tabla_clasificacion = cotizaciones.groupby("Clasificacion").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Semaforo=("Semaforo", "first")
).reset_index()

st.dataframe(tabla_clasificacion, use_container_width=True)

fig_clasificacion = px.bar(
    tabla_clasificacion,
    x="Clasificacion",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Clasificación de Clientes",
    labels={"Total_Monto": "Monto Total", "Clasificacion": "Clasificación", "Promedio_Avance": "Avance Promedio"},
    text="Total_Cotizaciones",
    color_continuous_scale="Viridis"
)
fig_clasificacion.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_clasificacion.update_layout(xaxis_title="Clasificación", yaxis_title="Monto Total")
st.plotly_chart(fig_clasificacion)

# Exportar Datos Procesados
st.subheader("Exportar Datos Procesados")

# Exportar datos procesados
data_to_export = cotizaciones.copy()
st.download_button(
    label="Descargar Datos Procesados",
    data=data_to_export.to_csv(index=False).encode("utf-8"),
    file_name="cotizaciones_procesadas.csv",
    mime="text/csv"
)
# Continuación del dashboard: Parte 3
st.header("Filtros Dinámicos y Distribución de Datos")

# Filtros Dinámicos
st.subheader("Explorar Cotizaciones con Filtros Dinámicos")

# Filtro por cliente
cliente_seleccionado = st.selectbox(
    "Selecciona un cliente para filtrar:", ["Todos"] + cotizaciones["Cliente"].unique().tolist()
)

# Filtro por área
area_seleccionada = st.selectbox(
    "Selecciona un área para filtrar:", ["Todos"] + cotizaciones["Area"].unique().tolist()
)

# Aplicar filtros
datos_filtrados = cotizaciones.copy()
if cliente_seleccionado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Cliente"] == cliente_seleccionado]
if area_seleccionada != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Area"] == area_seleccionada]

# Mostrar resultados filtrados
st.write("Resultados Filtrados:")
st.dataframe(datos_filtrados, use_container_width=True)

# Distribución de Montos Filtrados
st.subheader("Distribución de Montos Filtrados")
if not datos_filtrados.empty:
    fig_distribucion = px.histogram(
        datos_filtrados,
        x="Monto",
        nbins=20,
        title="Distribución de Montos Filtrados",
        labels={"Monto": "Monto Total"},
        color_discrete_sequence=["blue"]
    )
    fig_distribucion.update_layout(xaxis_title="Monto", yaxis_title="Frecuencia")
    st.plotly_chart(fig_distribucion)
else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")

# Editar Datos
st.subheader("Edición Interactiva de Datos")

# Selección de columna para editar
columna_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Avance_Porcentaje"])

# Nueva entrada para la columna seleccionada
nuevo_valor = st.text_input("Introduce un nuevo valor para la columna seleccionada:")
if st.button("Aplicar Cambios"):
    if columna_editar in datos_filtrados.columns:
        datos_filtrados[columna_editar] = nuevo_valor
        st.success(f"Los valores de la columna {columna_editar} se han actualizado correctamente.")
    else:
        st.error("No se puede editar la columna seleccionada.")

# Resumen de Avances
st.subheader("Resumen de Avances por Semáforo")
resumen_semaforo = datos_filtrados.groupby("Semaforo").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Monto_Total=("Monto", "sum")
).reset_index()

st.dataframe(resumen_semaforo, use_container_width=True)

# Exportar Datos Filtrados
st.subheader("Exportar Resultados Filtrados")
if not datos_filtrados.empty:
    st.download_button(
        label="Descargar Datos Filtrados",
        data=datos_filtrados.to_csv(index=False).encode("utf-8"),
        file_name="cotizaciones_filtradas.csv",
        mime="text/csv"
    )
else:
    st.warning("No hay datos disponibles para exportar.")

# Continuación del dashboard: Parte 4
st.header("Reporte Consolidado y Análisis Final")

# Tabla Consolidada por Estado
st.subheader("Resumen por Estado")

tabla_estado = cotizaciones.groupby("Estatus").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Semaforo=("Semaforo", "first")
).reset_index()

st.dataframe(tabla_estado, use_container_width=True)

fig_estado = px.bar(
    tabla_estado,
    x="Estatus",
    y="Total_Monto",
    color="Semaforo",
    title="Monto Total por Estado",
    labels={"Total_Monto": "Monto Total", "Estatus": "Estado"},
    text="Total_Cotizaciones",
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_estado.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_estado.update_layout(xaxis_title="Estado", yaxis_title="Monto Total")
st.plotly_chart(fig_estado)

# Pronóstico Anual Consolidado
st.subheader("Pronóstico Anual Consolidado")

if "2020" in cotizaciones.columns and "2021" in cotizaciones.columns:
    pronostico_anual = pd.DataFrame({
        "Año": ["2020", "2021"],
        "Monto": [
            cotizaciones["2020"].sum(),
            cotizaciones["2021"].sum()
        ]
    })
else:
    pronostico_anual = pd.DataFrame({
        "Año": ["2020", "2021"],
        "Monto": [2000000, 3000000]  # Valores simulados
    })

fig_pronostico_anual = px.line(
    pronostico_anual,
    x="Año",
    y="Monto",
    title="Pronóstico Anual Consolidado",
    labels={"Monto": "Monto Total", "Año": "Año"},
    markers=True
)
fig_pronostico_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total")
st.plotly_chart(fig_pronostico_anual)

# Exportar Reporte Consolidado
st.subheader("Exportar Reporte Consolidado")

import io
from pandas import ExcelWriter

output = io.BytesIO()
with ExcelWriter(output, engine="xlsxwriter") as writer:
    cotizaciones.to_excel(writer, sheet_name="Cotizaciones", index=False)
    tabla_estado.to_excel(writer, sheet_name="Resumen_Estado", index=False)
    pronostico_anual.to_excel(writer, sheet_name="Pronostico_Anual", index=False)
    writer.save()

output.seek(0)
st.download_button(
    label="Descargar Reporte Consolidado",
    data=output,
    file_name="reporte_consolidado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.info("Reporte consolidado generado con éxito. Revisa las proyecciones y resúmenes para decisiones informadas.")
