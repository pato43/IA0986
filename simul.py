import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📈",
    layout="wide"
)

# Título del dashboard
st.title("Dashboard de Automatización de Cotizaciones")
st.markdown(
    """
    Este dashboard permite gestionar, analizar y pronosticar las cotizaciones de manera eficiente. Puedes editar datos esenciales, visualizar tendencias y realizar análisis profundos.
    """
)

# Lectura del archivo cleaned_coti.csv
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    datos = pd.read_csv(file_path)
    return datos

cotizaciones = cargar_datos(FILE_PATH)

# Clonar DataFrame para ediciones
cotizaciones_editables = cotizaciones.copy()

# Validar y convertir columnas relevantes
numericas = ["Monto", "Avance_Porcentaje"]
for col in numericas:
    cotizaciones_editables[col] = pd.to_numeric(cotizaciones_editables[col], errors="coerce")

# Layout inicial
st.subheader("Vista General de Datos")
col1, col2 = st.columns([3, 1])
with col1:
    st.dataframe(cotizaciones_editables.head(), use_container_width=True)
with col2:
    st.metric("Total de Cotizaciones", len(cotizaciones_editables))

# Edición de datos esenciales
st.subheader("Editar Datos Esenciales")
columnas_editables = st.multiselect(
    "Selecciona las columnas a editar:",
    options=cotizaciones_editables.columns,
    default=["Cliente", "Concepto", "Monto", "Avance_Porcentaje", "Estatus"]
)

if columnas_editables:
    st.write("Edita los datos seleccionados directamente:")
    for columna in columnas_editables:
        st.markdown(f"### Editar columna: {columna}")
        if cotizaciones_editables[columna].dtype == "object":
            unique_values = cotizaciones_editables[columna].dropna().unique()
            nuevo_valor = st.text_input(f"Nuevo valor para {columna}")
            if st.button(f"Aplicar a {columna}"):
                cotizaciones_editables[columna] = cotizaciones_editables[columna].replace(unique_values, nuevo_valor)
                st.success(f"Valores en la columna {columna} actualizados.")
        elif cotizaciones_editables[columna].dtype in ["int64", "float64"]:
            min_val = st.number_input(f"Valor mínimo para {columna}", value=float(cotizaciones_editables[columna].min()))
            max_val = st.number_input(f"Valor máximo para {columna}", value=float(cotizaciones_editables[columna].max()))
            if st.button(f"Aplicar rango a {columna}"):
                cotizaciones_editables[columna] = cotizaciones_editables[columna].clip(lower=min_val, upper=max_val)
                st.success(f"Valores en la columna {columna} ajustados al rango especificado.")

# Determinación del estado del semáforo
st.subheader("Estados de Cotizaciones")
def asignar_estado(avance):
    if avance == 100:
        return "🟢 Aprobada"
    elif avance >= 50:
        return "🟡 Pendiente"
    else:
        return "🔴 Rechazada"

cotizaciones_editables["Estado_Semaforo"] = cotizaciones_editables["Avance_Porcentaje"].apply(asignar_estado)

# Tabla resumen por estado
st.write("Distribución de Estados de las Cotizaciones:")
estados_resumen = cotizaciones_editables["Estado_Semaforo"].value_counts().reset_index()
estados_resumen.columns = ["Estado", "Cantidad"]
col3, col4 = st.columns([2, 1])
with col3:
    st.dataframe(estados_resumen, use_container_width=True)
with col4:
    fig = px.bar(
        estados_resumen,
        x="Estado",
        y="Cantidad",
        title="Distribución de Estados de Cotizaciones",
        color="Estado",
        text="Cantidad",
        color_discrete_map={"🟢 Aprobada": "green", "🟡 Pendiente": "yellow", "🔴 Rechazada": "red"}
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig)

# Datos de cotizaciones 2020-2021
st.subheader("Análisis de Cotizaciones 2020-2021")
cotizaciones_editables["Año"] = pd.to_datetime(cotizaciones_editables["Fecha"], errors="coerce").dt.year

datos_2020_2021 = cotizaciones_editables[cotizaciones_editables["Año"].isin([2020, 2021])]
cotizaciones_anuales = datos_2020_2021.groupby("Año").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum")
).reset_index()

col5, col6 = st.columns([2, 1])
with col5:
    st.write("Resumen de Cotizaciones por Año:")
    st.dataframe(cotizaciones_anuales, use_container_width=True)

with col6:
    fig_anual = px.bar(
        cotizaciones_anuales,
        x="Año",
        y="Total_Monto",
        title="Monto Total por Año (2020-2021)",
        text="Total_Monto",
        color="Año",
        color_continuous_scale="Blues"
    )
    fig_anual.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_anual.update_layout(showlegend=False)
    st.plotly_chart(fig_anual)

# Pronóstico de ventas mensuales
st.subheader("Pronóstico de Ventas Mensuales")
mes_actual = cotizaciones_editables[pd.to_datetime(cotizaciones_editables["Fecha"], errors="coerce").dt.month == 12]
total_mes_actual = mes_actual["Monto"].sum()
st.metric(label="Ventas Estimadas para el Mes Actual", value=f"${total_mes_actual:,.2f}")
# Continuación del Dashboard: Parte 2

# Pronóstico Anual de Ventas
st.subheader("Pronóstico Anual de Ventas")

# Preparar datos de series de tiempo
ventas_mensuales = cotizaciones_editables.groupby(pd.to_datetime(cotizaciones_editables["Fecha"], errors="coerce").dt.to_period("M")).agg(
    Total_Monto=("Monto", "sum")
).reset_index()
ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

# Crear modelo de regresión lineal para predicciones
from sklearn.linear_model import LinearRegression
modelo = LinearRegression()
ventas_mensuales["Mes"] = np.arange(len(ventas_mensuales))
X = ventas_mensuales[["Mes"]]
y = ventas_mensuales["Total_Monto"]

# Verificar datos antes de ajustar
if not X.empty and not y.empty:
    modelo.fit(X, y)

    # Predicción para los próximos 12 meses
    meses_futuros = 12
    nuevos_meses = np.arange(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros).reshape(-1, 1)
    predicciones = modelo.predict(nuevos_meses)

    # Combinar datos históricos y pronosticados
    futuras_fechas = pd.date_range(ventas_mensuales["Fecha"].iloc[-1] + pd.DateOffset(months=1), periods=meses_futuros, freq="M")
    datos_pronostico = pd.DataFrame({
        "Fecha": futuras_fechas,
        "Total_Monto": predicciones,
        "Tipo": "Pronóstico"
    })

    ventas_mensuales["Tipo"] = "Histórico"
    datos_completos = pd.concat([ventas_mensuales, datos_pronostico], ignore_index=True)

    # Gráfico de series de tiempo
    st.markdown("### Gráfico de Series de Tiempo para Ventas")
    fig = px.line(
        datos_completos,
        x="Fecha",
        y="Total_Monto",
        color="Tipo",
        title="Pronóstico Anual de Ventas",
        labels={"Total_Monto": "Monto Total", "Fecha": "Mes"}
    )
    st.plotly_chart(fig)
else:
    st.warning("Los datos no son suficientes para generar un modelo de pronóstico.")

# Resumen de Pronóstico Anual
st.subheader("Resumen de Pronóstico Anual")
promedio_pronostico = predicciones.mean() if 'predicciones' in locals() else 0
st.metric(label="Promedio Pronosticado Mensual", value=f"${promedio_pronostico:,.2f}")

# Sección de Exportación
st.subheader("Exportar Datos Procesados")
if not cotizaciones_editables.empty:
    st.download_button(
        label="Descargar Cotizaciones Actualizadas",
        data=cotizaciones_editables.to_csv(index=False).encode('utf-8'),
        file_name="cotizaciones_actualizadas.csv",
        mime="text/csv"
    )

# Tablas dinámicas para análisis
st.subheader("Análisis Dinámico de Cotizaciones")
# Agrupación por cliente
st.markdown("#### Agrupación por Cliente")
tabla_cliente = cotizaciones_editables.groupby("Cliente").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Cliente", "count")
).reset_index()
st.dataframe(tabla_cliente, use_container_width=True)

# Agrupación por estado
st.markdown("#### Agrupación por Estado de Semáforo")
tabla_estado = cotizaciones_editables.groupby("Estado_Semaforo").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Estado_Semaforo", "count")
).reset_index()
st.dataframe(tabla_estado, use_container_width=True)

# Final de la parte 2
st.markdown("---")
st.info("Esta sección concluye el análisis de pronósticos y agrupaciones dinámicas de cotizaciones.")
# Continuación del Dashboard: Parte 3

# Comparativa de Tendencias por Área
st.subheader("Tendencias de Cotización por Área")

# Agrupar datos por área
grafico_area = cotizaciones_editables.groupby("Area").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum")
).reset_index()

def graficar_por_area(datos):
    fig = px.bar(
        datos,
        x="Area",
        y="Total_Monto",
        color="Area",
        title="Monto Total de Cotizaciones por Área",
        labels={"Total_Monto": "Monto Total", "Area": "Área"},
        text="Total_Monto",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(xaxis_title="Área", yaxis_title="Monto Total", xaxis_tickangle=-45)
    st.plotly_chart(fig)

graficar_por_area(grafico_area)

# Comparativa entre Vendedores
st.subheader("Desempeño de Vendedores")

grafico_vendedores = cotizaciones_editables.groupby("Vendedor").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

def graficar_por_vendedor(datos):
    fig = px.bar(
        datos,
        x="Vendedor",
        y="Total_Monto",
        color="Promedio_Avance",
        title="Monto Total de Cotizaciones por Vendedor",
        labels={"Total_Monto": "Monto Total", "Vendedor": "Vendedor", "Promedio_Avance": "Avance Promedio"},
        text="Total_Monto",
        color_continuous_scale="Bluered"
    )
    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig.update_layout(xaxis_title="Vendedor", yaxis_title="Monto Total", xaxis_tickangle=-45)
    st.plotly_chart(fig)

graficar_por_vendedor(grafico_vendedores)

# Filtros Dinámicos para Cotizaciones
st.subheader("Explorar Cotizaciones con Filtros Dinámicos")

# Filtro por cliente
cliente_seleccionado = st.selectbox(
    "Selecciona un cliente para filtrar:", options=["Todos"] + list(cotizaciones_editables["Cliente"].unique())
)

# Filtro por estado de semáforo
estado_seleccionado = st.selectbox(
    "Selecciona un estado para filtrar:", options=["Todos"] + list(cotizaciones_editables["Estado_Semaforo"].unique())
)

# Aplicar filtros
filtros = cotizaciones_editables.copy()
if cliente_seleccionado != "Todos":
    filtros = filtros[filtros["Cliente"] == cliente_seleccionado]
if estado_seleccionado != "Todos":
    filtros = filtros[filtros["Estado_Semaforo"] == estado_seleccionado]

# Mostrar resultados filtrados
st.write("Resultados Filtrados:")
st.dataframe(filtros, use_container_width=True)

# Gráfico dinámico basado en filtros
if not filtros.empty:
    st.subheader("Distribución de Montos Filtrados")
    fig = px.histogram(
        filtros,
        x="Monto",
        nbins=15,
        title="Distribución de Montos Filtrados",
        labels={"Monto": "Monto"},
        color_discrete_sequence=["blue"]
    )
    fig.update_layout(xaxis_title="Monto", yaxis_title="Frecuencia")
    st.plotly_chart(fig)
else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")

# Evaluación de Desempeño por Clasificación
st.subheader("Desempeño por Clasificación de Clientes")

grafico_clasificacion = cotizaciones_editables.groupby("Clasificacion").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

fig = px.bar(
    grafico_clasificacion,
    x="Clasificacion",
    y="Total_Monto",
    color="Promedio_Avance",
    title="Monto Total por Clasificación de Clientes",
    labels={"Total_Monto": "Monto Total", "Clasificacion": "Clasificación", "Promedio_Avance": "Avance Promedio"},
    text="Total_Monto",
    color_continuous_scale="Viridis"
)
fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig.update_layout(xaxis_title="Clasificación", yaxis_title="Monto Total")
st.plotly_chart(fig)

# Finalización
st.markdown("---")
st.info("Concluimos el análisis dinámico y exploración de cotizaciones. Utiliza las herramientas para tomar decisiones informadas.")
