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
@st.cache_data
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
Este dashboard permite gestionar cotizaciones de manera eficiente, con funcionalidad para edición de datos, 
comentarios, análisis y generación de reportes automatizados.
""")

# Tabla principal
st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]
st.dataframe(cotizaciones[columnas_mostrar], use_container_width=True)

# Filtros interactivos
st.subheader("Filtrar por Estado del Semáforo")
semaforo_seleccionado = st.selectbox(
    "Selecciona el estado del semáforo:",
    ["Todos"] + cotizaciones["Semaforo"].unique().tolist()
)

if semaforo_seleccionado != "Todos":
    cotizaciones_filtradas = cotizaciones[cotizaciones["Semaforo"] == semaforo_seleccionado]
else:
    cotizaciones_filtradas = cotizaciones

st.dataframe(cotizaciones_filtradas[columnas_mostrar], use_container_width=True)

# Métricas principales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones))
col2.metric("Monto Total", f"${cotizaciones['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones['DIAS'].mean():.2f}")

# Sección de comentarios por cliente
st.subheader("Comentarios por Cliente")
cliente_comentarios = st.selectbox("Selecciona un cliente para ver o editar comentarios:", cotizaciones["CLIENTE"].unique())
comentario_actual = cotizaciones[cotizaciones["CLIENTE"] == cliente_comentarios]["Comentarios"].values[0]
nuevo_comentario = st.text_area("Comentario Actual:", comentario_actual)
if st.button("Actualizar Comentario"):
    cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_comentarios, "Comentarios"] = nuevo_comentario
    st.success("Comentario actualizado correctamente.")

# Gráfico de distribución por método de captura
if "LLAMADA AL CLIENTE" in cotizaciones.columns:
    st.subheader("Distribución por Método de Captura")
    fig_metodos = px.bar(
        cotizaciones.groupby("LLAMADA AL CLIENTE").size().reset_index(name="Cantidad"),
        x="LLAMADA AL CLIENTE",
        y="Cantidad",
        color="LLAMADA AL CLIENTE",
        title="Cantidad de Cotizaciones por Método de Captura",
        labels={"LLAMADA AL CLIENTE": "Método de Captura", "Cantidad": "Número de Cotizaciones"}
    )
    fig_metodos.update_layout(xaxis_title="Método de Captura", yaxis_title="Cantidad")
    st.plotly_chart(fig_metodos)
else:
    st.warning("No se encontraron datos para los métodos de captura.")

# Generación de reportes automatizados
st.subheader("Reporte Automático de Cotizaciones Aprobadas")
reporte_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not reporte_aprobadas.empty:
    st.write("Cotizaciones aprobadas disponibles para descarga:")
    st.dataframe(reporte_aprobadas[columnas_mostrar], use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=reporte_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas actualmente.")
