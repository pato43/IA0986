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
# Continuación del Dashboard: Parte 2

# Sección: Edición de Datos de Clientes
st.subheader("Edición de Datos de Clientes")
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["CLIENTE"].unique())
columna_a_editar = st.selectbox(
    "Selecciona una columna para editar:",
    ["MONTO", "ESTATUS", "LLAMADA AL CLIENTE", "DIAS", "Comentarios"]
)
nuevo_valor = st.text_input("Introduce el nuevo valor para la columna seleccionada:")
if st.button("Aplicar Cambios"):
    try:
        if columna_a_editar in ["MONTO", "DIAS"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_a_editar, columna_a_editar] = nuevo_valor
        st.success("¡Los cambios se han aplicado correctamente!")
    except ValueError:
        st.error("El valor ingresado no es válido para la columna seleccionada.")

# Análisis por Vendedor
st.subheader("Análisis por Vendedor")
tabla_vendedores = cotizaciones.groupby("VENDEDOR").agg(
    Total_Cotizaciones=("CLIENTE", "count"),
    Total_Monto=("MONTO", "sum"),
    Promedio_Avance=("DIAS", "mean")
).reset_index()

st.dataframe(tabla_vendedores, use_container_width=True)

fig_vendedores = px.bar(
    tabla_vendedores,
    x="VENDEDOR",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Vendedor",
    labels={"Total_Monto": "Monto Total", "VENDEDOR": "Vendedor", "Promedio_Avance": "Promedio de Días"},
    text="Total_Cotizaciones",
    color_continuous_scale="Viridis"
)
fig_vendedores.update_layout(xaxis_title="Vendedor", yaxis_title="Monto Total", xaxis_tickangle=-45)
st.plotly_chart(fig_vendedores)

# Reporte automático de cotizaciones aprobadas
st.subheader("Reporte Automático de Cotizaciones Aprobadas")
reporte_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not reporte_aprobadas.empty:
    st.write("Cotizaciones aprobadas disponibles para descarga:")
    st.dataframe(reporte_aprobadas, use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=reporte_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas actualmente.")

# Gráfico: Distribución por Clasificación
st.subheader("Distribución por Clasificación de Clientes")
if "CLASIFICACION" in cotizaciones.columns:
    fig_clasificacion = px.pie(
        cotizaciones,
        names="CLASIFICACION",
        title="Distribución por Clasificación de Clientes",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_clasificacion)
else:
    st.warning("No se encontraron datos de clasificación para generar el gráfico.")

# Exportar Datos Completos
st.subheader("Exportar Datos Completos")
st.download_button(
    label="Descargar Datos Actualizados",
    data=cotizaciones.to_csv(index=False).encode("utf-8"),
    file_name="cotizaciones_actualizadas.csv",
    mime="text/csv"
)

# Métricas adicionales basadas en filtros
st.subheader("Métricas Filtradas")
monto_total_filtrado = cotizaciones_filtradas["MONTO"].sum()
promedio_dias_filtrado = cotizaciones_filtradas["DIAS"].mean()
col4, col5 = st.columns(2)
col4.metric("Monto Total Filtrado", f"${monto_total_filtrado:,.2f}")
col5.metric("Promedio de Días Filtrado", f"{promedio_dias_filtrado:.2f}")
