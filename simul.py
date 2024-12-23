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

    # Limpieza y procesamiento de datos
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

    # Procesamiento adicional
    df_copia["Metodo_Captura"] = df_copia["Cliente"].apply(
        lambda x: "Teléfono" if "A" in x else ("Correo" if "E" in x else "Internet")
    )
    df_copia["Duracion_Dias"] = df_copia["Duracion_Dias"].fillna(30)
    df_copia["Fecha_Envio"] = pd.to_datetime(df_copia["Fecha_Envio"], errors="coerce").fillna(pd.Timestamp.now())
    df_copia["Comentarios"] = df_copia.get("Comentarios", "Sin comentarios")
    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Sección inicial: Tabla general con semáforo
st.title("Dashboard de Cotizaciones")
st.markdown("Este dashboard permite gestionar cotizaciones de manera eficiente y realizar análisis detallados de los datos.")

st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA INICIO", "DIAS", "FECHA ENVIO", "MONTO",
    "ESTATUS", "LLAMADA AL CLIENTE", "Cotizado X CLIENTE", "$", "Vendedor", "N° de cotizaciones realizadas",
    "A", "AA", "AAA", "Acumulado cotizado Febrero 2021", "% Acumulado presente", "Cotizado del mes", "2020",
    "2021", "Pronostico con metodo de suavizacion exponencial", "COTIZADO POR ÁREA", "$", "PRONOSTICO X AREA",
    "COTIZADO", "VENTA", "CLIENTE", "CONCEPTO"
]

tabla_principal = cotizaciones.rename(columns={
    "Monto": "MONTO", "Cliente": "CLIENTE", "Estatus": "ESTATUS", "Fecha_Envio": "FECHA ENVIO",
    "Metodo_Captura": "LLAMADA AL CLIENTE", "Duracion_Dias": "DIAS"
})

st.dataframe(tabla_principal[columnas_mostrar], use_container_width=True)

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

# Función para agregar nuevos registros
st.subheader("Agregar Nuevo Registro de Cliente")
with st.form("form_agregar_cliente"):
    nuevo_cliente = st.text_input("Nombre del Cliente")
    nuevo_monto = st.number_input("Monto", min_value=0.0, step=1000.0)
    nuevo_estatus = st.selectbox("Estatus", ["APROBADA", "PENDIENTE", "RECHAZADA"])
    nuevo_metodo = st.selectbox("Método de Captura", ["Teléfono", "Correo", "Internet"])
    nueva_duracion = st.number_input("Duración en Días", min_value=1, step=1)
    nueva_fecha_envio = st.date_input("Fecha de Envío")
    nuevo_comentario = st.text_area("Comentarios del Cliente")
    agregar_cliente = st.form_submit_button("Agregar Cliente")

if agregar_cliente:
    nuevo_registro = {
        "CLIENTE": nuevo_cliente,
        "MONTO": nuevo_monto,
        "ESTATUS": nuevo_estatus,
        "Semaforo": "🟢 Aprobada" if nuevo_estatus == "APROBADA" else ("🟡 Pendiente" if nuevo_estatus == "PENDIENTE" else "🔴 Rechazada"),
        "LLAMADA AL CLIENTE": nuevo_metodo,
        "DIAS": nueva_duracion,
        "FECHA ENVIO": nueva_fecha_envio,
        "Comentarios": nuevo_comentario
    }
    cotizaciones = cotizaciones.append(nuevo_registro, ignore_index=True)
    st.success("Nuevo registro agregado exitosamente.")

# Sección de comentarios
st.subheader("Comentarios por Cliente")
cliente_seleccionado_comentarios = st.selectbox("Selecciona un cliente para visualizar comentarios:", cotizaciones["Cliente"].unique())
comentarios_cliente = cotizaciones[cotizaciones["Cliente"] == cliente_seleccionado_comentarios]["Comentarios"].values[0]
st.text_area("Comentarios:", comentarios_cliente, height=150)
# Continuación del Dashboard: Parte 2
import plotly.graph_objects as go

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
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["CLIENTE"].unique())
columna_a_editar = st.selectbox("Selecciona una columna para editar:", ["MONTO", "ESTATUS", "LLAMADA AL CLIENTE", "DIAS", "Comentarios"])
nuevo_valor = st.text_input("Introduce el nuevo valor:")
if st.button("Aplicar Cambios"):
    try:
        if columna_a_editar in ["MONTO", "DIAS"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_a_editar, columna_a_editar] = nuevo_valor
        st.success("¡El cambio ha sido aplicado con éxito!")
    except ValueError:
        st.error("El valor introducido no es válido para la columna seleccionada.")

# Análisis por Vendedor
st.subheader("Análisis por Vendedor")
tabla_vendedores = cotizaciones.groupby("VENDEDOR").agg(
    Total_Cotizaciones=("CLIENTE", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

st.dataframe(tabla_vendedores, use_container_width=True)

fig_vendedores = px.bar(
    tabla_vendedores,
    x="VENDEDOR",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Vendedor",
    labels={"Total_Monto": "Monto Total", "VENDEDOR": "Vendedor", "Promedio_Avance": "Avance Promedio"},
    text="Total_Cotizaciones",
    color_continuous_scale="Bluered"
)
fig_vendedores.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_vendedores.update_layout(xaxis_title="Vendedor", yaxis_title="Monto Total", xaxis_tickangle=-45)
st.plotly_chart(fig_vendedores)

# Distribución de Montos por Cliente
st.subheader("Distribución de Montos por Cliente")
fig_distribucion_cliente = px.histogram(
    cotizaciones,
    x="CLIENTE",
    y="Monto",
    title="Distribución de Montos por Cliente",
    labels={"CLIENTE": "Cliente", "Monto": "Monto Total"},
    color_discrete_sequence=["blue"]
)
fig_distribucion_cliente.update_layout(xaxis_title="Cliente", yaxis_title="Monto Total", xaxis_tickangle=-45)
st.plotly_chart(fig_distribucion_cliente)

# Exportar Datos Actualizados
st.subheader("Exportar Datos")
st.download_button(
    label="Descargar Datos Actualizados",
    data=cotizaciones.to_csv(index=False).encode("utf-8"),
    file_name="cotizaciones_actualizadas.csv",
    mime="text/csv"
)

# Reporte Automático al Detectar Nuevas Aprobaciones
st.subheader("Reporte Automático")
nuevas_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not nuevas_aprobadas.empty:
    st.write("Nuevas cotizaciones aprobadas:")
    st.dataframe(nuevas_aprobadas, use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Aprobaciones",
        data=nuevas_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_aprobaciones.csv",
        mime="text/csv"
    )
