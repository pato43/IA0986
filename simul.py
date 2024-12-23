import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Cargar y procesar datos
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Limpieza y simulación de datos faltantes
    df_copia["Monto"] = pd.to_numeric(df_copia["Monto"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(100000)
    df_copia["Avance_Porcentaje"] = pd.to_numeric(df_copia["Avance_Porcentaje"], errors="coerce").fillna(50)
    df_copia["2020"] = pd.to_numeric(df_copia["2020"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(2000000)
    df_copia["2021"] = pd.to_numeric(df_copia["2021"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(3000000)
    df_copia["Estatus"] = df_copia["Estatus"].fillna("Desconocido")
    df_copia["Cliente"] = df_copia["Cliente"].fillna("Cliente_Desconocido")

    # Agregar semáforo dinámico
    df_copia["Semaforo"] = df_copia["Estatus"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Simular datos adicionales
    df_copia["Metodo_Captura"] = df_copia["Cliente"].apply(
        lambda x: "Teléfono" if "A" in x else ("Correo" if "E" in x else "Internet")
    )
    df_copia["Duracion_Dias"] = df_copia["Duracion_Dias"].fillna(30)
    df_copia["Fecha_Envio"] = pd.to_datetime(df_copia["Fecha_Envio"], errors="coerce").fillna(pd.Timestamp.now())
    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Sección inicial: Tabla general con semáforo
st.title("Dashboard de Cotizaciones")
st.markdown("Este dashboard permite gestionar cotizaciones de manera eficiente, incluyendo simulación de datos donde sea necesario.")

st.subheader("Estado General de Clientes")
st.dataframe(
    cotizaciones[["Cliente", "Monto", "Estatus", "Semaforo", "Metodo_Captura", "Duracion_Dias", "Fecha_Envio"]],
    use_container_width=True
)

# Métricas principales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones))
col2.metric("Monto Total", f"${cotizaciones['Monto'].sum():,.2f}")
col3.metric("Promedio de Avance", f"{cotizaciones['Avance_Porcentaje'].mean():.2f}%")

# Gráfico de Distribución por Método de Captura
st.subheader("Distribución por Método de Captura")
fig_captura = px.bar(
    cotizaciones.groupby("Metodo_Captura").size().reset_index(name="Cantidad"),
    x="Metodo_Captura",
    y="Cantidad",
    color="Metodo_Captura",
    title="Métodos de Captura de Cotizaciones",
    labels={"Cantidad": "Cantidad de Cotizaciones", "Metodo_Captura": "Método de Captura"},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_captura.update_traces(textposition="outside")
fig_captura.update_layout(xaxis_title="Método", yaxis_title="Cantidad")
st.plotly_chart(fig_captura)

# Gráfico de Montos por Semáforo
st.subheader("Montos por Semáforo de Estatus")
fig_semaforo = px.bar(
    cotizaciones.groupby("Semaforo").agg(Monto_Total=("Monto", "sum")).reset_index(),
    x="Semaforo",
    y="Monto_Total",
    color="Semaforo",
    title="Montos Totales por Semáforo",
    labels={"Monto_Total": "Monto Total", "Semaforo": "Estado del Semáforo"},
    color_discrete_map={"🟢 Aprobada": "green", "🟡 Pendiente": "yellow", "🔴 Rechazada": "red"}
)
fig_semaforo.update_layout(xaxis_title="Semáforo", yaxis_title="Monto Total")
st.plotly_chart(fig_semaforo)

# Edición interactiva de datos
st.subheader("Edición de Datos de Clientes")
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["Cliente"].unique())
columna_a_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Metodo_Captura", "Duracion_Dias"])
nuevo_valor = st.text_input("Introduce el nuevo valor:")
if st.button("Aplicar Cambios"):
    try:
        if columna_a_editar in ["Monto", "Duracion_Dias"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones.loc[cotizaciones["Cliente"] == cliente_a_editar, columna_a_editar] = nuevo_valor
        st.success("¡El cambio ha sido aplicado con éxito!")
    except ValueError:
        st.error("El valor introducido no es válido para la columna seleccionada.")

# Continuación del dashboard: Parte 2
st.header("Análisis por Vendedor y Clasificación")

# Análisis por Vendedor
st.subheader("Desempeño por Vendedor")

tabla_vendedores = cotizaciones.groupby("Metodo_Captura").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

st.dataframe(tabla_vendedores, use_container_width=True)

fig_vendedores = px.bar(
    tabla_vendedores,
    x="Metodo_Captura",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Método de Captura",
    labels={"Total_Monto": "Monto Total", "Metodo_Captura": "Método de Captura", "Promedio_Avance": "Avance Promedio"},
    text="Total_Cotizaciones",
    color_continuous_scale="Bluered"
)
fig_vendedores.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_vendedores.update_layout(xaxis_title="Método de Captura", yaxis_title="Monto Total", xaxis_tickangle=-45)
st.plotly_chart(fig_vendedores)

# Análisis por Clasificación
st.subheader("Desempeño por Clasificación de Clientes")

tabla_clasificacion = cotizaciones.groupby("Estatus").agg(
    Total_Cotizaciones=("Cliente", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

st.dataframe(tabla_clasificacion, use_container_width=True)

fig_clasificacion = px.bar(
    tabla_clasificacion,
    x="Estatus",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Clasificación de Clientes",
    labels={"Total_Monto": "Monto Total", "Estatus": "Clasificación", "Promedio_Avance": "Avance Promedio"},
    text="Total_Cotizaciones",
    color_continuous_scale="Viridis"
)
fig_clasificacion.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_clasificacion.update_layout(xaxis_title="Clasificación", yaxis_title="Monto Total")
st.plotly_chart(fig_clasificacion)

# Exportar Datos Filtrados
st.subheader("Exportar Reporte de Análisis")
data_to_export = cotizaciones.copy()
st.download_button(
    label="Descargar Análisis",
    data=data_to_export.to_csv(index=False).encode("utf-8"),
    file_name="reporte_analisis.csv",
    mime="text/csv"
)

# Continuación del dashboard: Parte 3
st.header("Filtros Dinámicos y Edición de Datos")

# Filtros dinámicos
st.subheader("Explorar Cotizaciones con Filtros Dinámicos")

# Filtro por cliente
cliente_seleccionado = st.selectbox(
    "Selecciona un cliente para filtrar:", ["Todos"] + cotizaciones["Cliente"].unique().tolist()
)

# Filtro por estatus
estatus_seleccionado = st.selectbox(
    "Selecciona un estatus para filtrar:", ["Todos"] + cotizaciones["Estatus"].unique().tolist()
)

# Filtro por rango de montos
monto_min, monto_max = st.slider(
    "Selecciona el rango de montos:",
    min_value=float(cotizaciones["Monto"].min()),
    max_value=float(cotizaciones["Monto"].max()),
    value=(float(cotizaciones["Monto"].min()), float(cotizaciones["Monto"].max()))
)

# Aplicar filtros
datos_filtrados = cotizaciones.copy()
if cliente_seleccionado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Cliente"] == cliente_seleccionado]
if estatus_seleccionado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Estatus"] == estatus_seleccionado]
datos_filtrados = datos_filtrados[(datos_filtrados["Monto"] >= monto_min) & (datos_filtrados["Monto"] <= monto_max)]

# Mostrar resultados filtrados
st.write("Resultados Filtrados:")
st.dataframe(datos_filtrados, use_container_width=True)

# Métricas dinámicas basadas en filtros
st.subheader("Métricas Basadas en Filtros")
col1, col2, col3 = st.columns(3)
col1.metric("Cotizaciones Filtradas", len(datos_filtrados))
col2.metric("Monto Total Filtrado", f"${datos_filtrados['Monto'].sum():,.2f}")
col3.metric("Promedio de Avance", f"{datos_filtrados['Avance_Porcentaje'].mean():.2f}%")

# Edición de datos filtrados
st.subheader("Edición Interactiva de Datos")

# Selección de columna para editar
columna_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Metodo_Captura", "Duracion_Dias"])

# Nueva entrada para la columna seleccionada
nuevo_valor = st.text_input("Introduce un nuevo valor para la columna seleccionada:")
if st.button("Aplicar Cambios a Datos Filtrados"):
    try:
        if columna_editar in ["Monto", "Duracion_Dias"]:
            nuevo_valor = float(nuevo_valor)
        datos_filtrados[columna_editar] = nuevo_valor
        st.success(f"Los valores de la columna {columna_editar} se han actualizado correctamente.")
    except ValueError:
        st.error("El valor introducido no es válido para la columna seleccionada.")

# Gráfico: Distribución de Montos Filtrados
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

# Gráfico: Avance Promedio por Estatus
st.subheader("Avance Promedio por Estatus")
if not datos_filtrados.empty:
    fig_avance = px.bar(
        datos_filtrados.groupby("Estatus").agg(Avance_Promedio=("Avance_Porcentaje", "mean")).reset_index(),
        x="Estatus",
        y="Avance_Promedio",
        color="Estatus",
        title="Avance Promedio por Estatus",
        labels={"Avance_Promedio": "Promedio de Avance (%)", "Estatus": "Estatus"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_avance.update_layout(xaxis_title="Estatus", yaxis_title="Promedio de Avance (%)")
    st.plotly_chart(fig_avance)
else:
    st.warning("No hay datos suficientes para generar el gráfico de avance promedio.")

# Exportar resultados filtrados
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
