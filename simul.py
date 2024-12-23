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
