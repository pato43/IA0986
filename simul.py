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

# Funciones para cargar y procesar los datos
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

    # Simular columnas faltantes
    df_copia["AREA"] = df_copia.get("AREA", "General")
    df_copia["CLASIFICACION"] = df_copia.get("CLASIFICACION", "No clasificado")
    df_copia["VENDEDOR"] = df_copia.get("VENDEDOR", "Desconocido")
    df_copia["Cotizado X CLIENTE"] = df_copia.get("Cotizado X CLIENTE", 0)
    df_copia["Pronostico con metodo de suavizacion exponencial"] = df_copia.get(
        "Pronostico con metodo de suavizacion exponencial", "Pendiente"
    )

    # Agregar semáforo dinámico basado en el estatus
    df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Limpieza de datos
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar los datos
cotizaciones = cargar_datos(FILE_PATH)

# Sección de introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard permite gestionar cotizaciones de manera eficiente, automatizar actualizaciones con el semáforo y 
realizar análisis detallados sobre los datos procesados.
""")

# Tabla principal con semáforo
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

# Gráfico de métodos de captura
st.subheader("Distribución por Método de Captura")
if "LLAMADA AL CLIENTE" in cotizaciones.columns:
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

# Sección de comentarios por cliente
st.subheader("Comentarios por Cliente")
cliente_comentarios = st.selectbox("Selecciona un cliente para ver o editar comentarios:", cotizaciones["CLIENTE"].unique())
comentario_actual = cotizaciones[cotizaciones["CLIENTE"] == cliente_comentarios].get("Comentarios", "Sin comentarios").values[0]
nuevo_comentario = st.text_area("Comentario Actual:", comentario_actual)
if st.button("Actualizar Comentario"):
    cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_comentarios, "Comentarios"] = nuevo_comentario
    st.success("Comentario actualizado correctamente.")
# Continuación del Dashboard: Parte 2

# Sección: Edición de datos de clientes
st.subheader("Edición de Datos de Clientes")
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["CLIENTE"].unique())
columna_a_editar = st.selectbox(
    "Selecciona una columna para editar:", ["MONTO", "ESTATUS", "LLAMADA AL CLIENTE", "DIAS", "Comentarios"]
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

# Análisis por vendedor
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
nuevas_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not nuevas_aprobadas.empty:
    st.write("Se han identificado nuevas cotizaciones aprobadas:")
    st.dataframe(nuevas_aprobadas, use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=nuevas_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_aprobaciones.csv",
        mime="text/csv"
    )
else:
    st.info("No se han encontrado nuevas cotizaciones aprobadas.")

# Exportar datos completos
st.subheader("Exportar Datos Completos")
st.download_button(
    label="Descargar Datos Actuales",
    data=cotizaciones.to_csv(index=False).encode("utf-8"),
    file_name="cotizaciones_actualizadas.csv",
    mime="text/csv"
)

# Sección: Análisis de Pronósticos
st.subheader("Pronóstico de Ventas")

def preparar_datos_pronostico(df, columna_tiempo="FECHA ENVIO", columna_valor="MONTO"):
    df[columna_tiempo] = pd.to_datetime(df[columna_tiempo], errors="coerce")
    df = df.groupby(df[columna_tiempo].dt.to_period("M"))[columna_valor].sum().reset_index()
    df[columna_tiempo] = df[columna_tiempo].dt.to_timestamp()
    return df

datos_pronostico = preparar_datos_pronostico(cotizaciones)

# Validación de datos para pronóstico
if len(datos_pronostico) < 12:
    st.warning("Datos insuficientes para pronóstico completo. Se están simulando datos adicionales.")
    meses_faltantes = 12 - len(datos_pronostico)
    fechas_simuladas = [
        datos_pronostico["FECHA ENVIO"].max() + pd.DateOffset(months=i + 1)
        for i in range(meses_faltantes)
    ]
    montos_simulados = [datos_pronostico["MONTO"].mean() for _ in range(meses_faltantes)]
    datos_simulados = pd.DataFrame({"FECHA ENVIO": fechas_simuladas, "MONTO": montos_simulados})
    datos_pronostico = pd.concat([datos_pronostico, datos_simulados]).reset_index(drop=True)
    datos_pronostico = datos_pronostico.sort_values(by="FECHA ENVIO")

# Gráfico: Pronóstico de ventas mensuales
st.subheader("Pronóstico de Ventas Mensuales")
fig_pronostico_mensual = px.line(
    datos_pronostico,
    x="FECHA ENVIO",
    y="MONTO",
    title="Pronóstico de Ventas Mensuales",
    labels={"FECHA ENVIO": "Mes", "MONTO": "Monto Total"},
    markers=True
)
fig_pronostico_mensual.update_layout(xaxis_title="Mes", yaxis_title="Monto Total")
st.plotly_chart(fig_pronostico_mensual)

# Pronóstico consolidado anual
st.subheader("Pronóstico de Ventas Anual Consolidado")
montos_anuales = [
    datos_pronostico["MONTO"].sum(),  # Total del año actual
    datos_pronostico["MONTO"].sum() * 1.1  # Proyección de crecimiento del 10%
]
anios = [2023, 2024]
fig_pronostico_anual = px.bar(
    x=anios,
    y=montos_anuales,
    title="Pronóstico Anual Consolidado",
    labels={"x": "Año", "y": "Monto Total"},
    color_discrete_sequence=["blue"]
)
fig_pronostico_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total")
st.plotly_chart(fig_pronostico_anual)

# Sección: Pronóstico del próximo mes
st.subheader("Pronóstico para el Próximo Mes")
ultimo_mes = datos_pronostico["FECHA ENVIO"].iloc[-1]
proximo_mes = ultimo_mes + pd.DateOffset(months=1)
proximo_valor = datos_pronostico["MONTO"].mean()
st.metric(
    label=f"Pronóstico para {proximo_mes.strftime('%B %Y')}",
    value=f"${proximo_valor:,.2f}",
    delta=f"+10% (estimado)"
)
