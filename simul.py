import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración inicial de la página
st.set_page_config(page_title="Simulación de Eventos y Análisis", layout="wide")
st.title("Simulación y Análisis de Eventos")
st.markdown("Esta aplicación permite explorar datos simulados, realizar análisis temporales y visualizar resultados interactivos.")

# Función para generar datos simulados
def generar_datos_simulados():
    np.random.seed(42)
    fechas = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
    eventos = np.random.poisson(lam=3, size=len(fechas))
    categorias = ["A", "B", "C"]
    categorias_aleatorias = np.random.choice(categorias, size=len(fechas))
    valores = np.random.uniform(10, 100, size=len(fechas))
    return pd.DataFrame({
        "Fecha": fechas,
        "Eventos": eventos,
        "Categoría": categorias_aleatorias,
        "Valor": valores
    })

# Función para crear un gráfico de dispersión
def crear_grafico_dispersión(data):
    fig = px.scatter(
        data,
        x="Fecha",
        y="Valor",
        color="Categoría",
        size="Eventos",
        title="Gráfico de Dispersión: Valor vs Fecha",
        labels={"Valor": "Monto", "Fecha": "Fecha"}
    )
    fig.update_layout(autosize=True, template="plotly_white")
    return fig

# Función para crear un gráfico de barras
def crear_grafico_barras(data):
    resumen = data.groupby("Categoría").agg({"Eventos": "sum", "Valor": "mean"}).reset_index()
    fig = px.bar(
        resumen,
        x="Categoría",
        y="Eventos",
        color="Categoría",
        title="Total de Eventos por Categoría",
        text_auto=True
    )
    fig.update_layout(autosize=True, template="plotly_white")
    return fig

# Función para simular datos futuros
def simular_datos_futuros(data, dias=30):
    ultima_fecha = data["Fecha"].max()
    nuevas_fechas = [ultima_fecha + timedelta(days=i) for i in range(1, dias + 1)]
    categorias = ["A", "B", "C"]
    nuevos_eventos = np.random.poisson(lam=3, size=len(nuevas_fechas))
    nuevas_categorias = np.random.choice(categorias, size=len(nuevas_fechas))
    nuevos_valores = np.random.uniform(10, 100, size=len(nuevas_fechas))
    nuevos_datos = pd.DataFrame({
        "Fecha": nuevas_fechas,
        "Eventos": nuevos_eventos,
        "Categoría": nuevas_categorias,
        "Valor": nuevos_valores
    })
    return pd.concat([data, nuevos_datos], ignore_index=True)

# Configuración de la barra lateral
st.sidebar.header("Opciones de Filtro")
categoria_seleccionada = st.sidebar.selectbox("Selecciona una Categoría", ["Todas", "A", "B", "C"])
rango_fechas = st.sidebar.date_input(
    "Rango de Fechas",
    value=[datetime(2023, 1, 1), datetime(2023, 12, 31)]
)
simular_dias = st.sidebar.slider("Simular Días Futuros", min_value=0, max_value=60, value=30)

# Generar y filtrar datos
datos_simulados = generar_datos_simulados()
if categoria_seleccionada != "Todas":
    datos_simulados = datos_simulados[datos_simulados["Categoría"] == categoria_seleccionada]
datos_simulados = datos_simulados[
    (datos_simulados["Fecha"] >= pd.to_datetime(rango_fechas[0])) &
    (datos_simulados["Fecha"] <= pd.to_datetime(rango_fechas[1]))
]

# Mostrar datos simulados
st.subheader("Datos Simulados Filtrados")
st.dataframe(datos_simulados)

# Visualización inicial: Gráfico de dispersión
st.subheader("Visualización: Gráfico de Dispersión")
grafico_dispersion = crear_grafico_dispersión(datos_simulados)
st.plotly_chart(grafico_dispersion, use_container_width=True)

# Visualización adicional: Gráfico de barras
st.subheader("Visualización: Gráfico de Barras")
grafico_barras = crear_grafico_barras(datos_simulados)
st.plotly_chart(grafico_barras, use_container_width=True)

# Simulación de datos futuros
st.subheader("Simulación de Datos Futuros")
if simular_dias > 0:
    datos_futuros = simular_datos_futuros(datos_simulados, dias=simular_dias)
    st.write(f"Datos simulados para los próximos {simular_dias} días:")
    st.dataframe(datos_futuros.tail(simular_dias))
    st.markdown("#### Visualización de Datos Simulados")
    grafico_dispersión_futuro = crear_grafico_dispersión(datos_futuros)
    st.plotly_chart(grafico_dispersión_futuro, use_container_width=True)
else:
    st.write("No se seleccionaron días para simular.")

# Indicador de progreso general
st.sidebar.markdown("---")
st.sidebar.info("Configuración Completa: Parte 1 del Proyecto")

# Mensaje de continuación
st.markdown("Continúa en la Parte 2 para análisis avanzado, correlaciones y predicciones.")
# Parte 2 - Análisis Avanzado y Predicciones

# Función para analizar correlaciones
def calcular_correlaciones(data):
    correlacion = data.corr(numeric_only=True)
    fig = px.imshow(
        correlacion,
        text_auto=True,
        title="Mapa de Calor: Correlaciones entre Variables",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(autosize=True, template="plotly_white")
    return fig

# Función para análisis de series de tiempo
def analizar_series_tiempo(data):
    resumen = data.groupby("Fecha")["Valor"].sum().reset_index()
    fig = px.line(
        resumen,
        x="Fecha",
        y="Valor",
        title="Análisis de Series de Tiempo: Valor Diario Total",
        labels={"Valor": "Monto Total", "Fecha": "Fecha"}
    )
    fig.update_layout(autosize=True, template="plotly_white")
    return fig

# Función para predicciones simples (promedio móvil)
def prediccion_promedio_movil(data, ventanas=7):
    resumen = data.groupby("Fecha")["Valor"].sum().reset_index()
    resumen["Promedio Móvil"] = resumen["Valor"].rolling(window=ventanas).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=resumen["Fecha"], y=resumen["Valor"], mode="lines", name="Valor Real"))
    fig.add_trace(go.Scatter(x=resumen["Fecha"], y=resumen["Promedio Móvil"], mode="lines", name=f"Promedio Móvil ({ventanas} días)"))
    fig.update_layout(
        title=f"Predicción Simple: Promedio Móvil ({ventanas} días)",
        xaxis_title="Fecha",
        yaxis_title="Monto Total",
        template="plotly_white",
        autosize=True
    )
    return fig

# Visualización: Mapa de calor de correlaciones
st.subheader("Análisis de Correlaciones")
grafico_correlacion = calcular_correlaciones(datos_simulados)
st.plotly_chart(grafico_correlacion, use_container_width=True)

# Visualización: Series de tiempo
st.subheader("Análisis de Series de Tiempo")
grafico_series_tiempo = analizar_series_tiempo(datos_simulados)
st.plotly_chart(grafico_series_tiempo, use_container_width=True)

# Predicciones: Promedio móvil
st.subheader("Predicción: Promedio Móvil")
ventanas_prediccion = st.slider("Ventana para Promedio Móvil (días)", min_value=3, max_value=30, value=7)
grafico_prediccion = prediccion_promedio_movil(datos_simulados, ventanas=ventanas_prediccion)
st.plotly_chart(grafico_prediccion, use_container_width=True)

# Análisis por categoría
st.subheader("Análisis Detallado por Categoría")
categoria_analisis = st.selectbox("Selecciona una Categoría para el Análisis Detallado", ["A", "B", "C"])
datos_categoria = datos_simulados[datos_simulados["Categoría"] == categoria_analisis]
st.write(f"Datos de la Categoría {categoria_analisis}")
st.dataframe(datos_categoria)

# Función para análisis de eventos por categoría
def grafico_eventos_categoria(data):
    resumen = data.groupby("Fecha")["Eventos"].sum().reset_index()
    fig = px.area(
        resumen,
        x="Fecha",
        y="Eventos",
        title=f"Eventos por Día en Categoría {categoria_analisis}",
        labels={"Eventos": "Número de Eventos", "Fecha": "Fecha"},
        color_discrete_sequence=["#636EFA"]
    )
    fig.update_layout(autosize=True, template="plotly_white")
    return fig

# Visualización de eventos por categoría
grafico_eventos = grafico_eventos_categoria(datos_categoria)
st.plotly_chart(grafico_eventos, use_container_width=True)

# Exportar datos simulados
st.subheader("Exportar Datos")
exportar_datos = st.checkbox("¿Deseas exportar los datos simulados?")
if exportar_datos:
    csv = datos_simulados.to_csv(index=False)
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name="datos_simulados.csv",
        mime="text/csv"
    )
    st.success("¡Datos listos para descargar!")

# Simulación adicional: Eventos extremos
st.subheader("Simulación de Eventos Extremos")
agregar_eventos_extremos = st.checkbox("¿Agregar eventos extremos a la simulación?")
if agregar_eventos_extremos:
    extremos = pd.DataFrame({
        "Fecha": [datetime(2023, 6, 15), datetime(2023, 11, 20)],
        "Eventos": [50, 80],
        "Categoría": ["A", "B"],
        "Valor": [1000, 2000]
    })
    datos_extremos = pd.concat([datos_simulados, extremos], ignore_index=True)
    st.write("Datos con eventos extremos agregados:")
    st.dataframe(datos_extremos)
    grafico_extremos = crear_grafico_dispersión(datos_extremos)
    st.plotly_chart(grafico_extremos, use_container_width=True)

# Mensaje final
st.sidebar.markdown("---")
st.sidebar.success("Parte 2 completada: Análisis y Predicciones")
st.markdown("**¡Gracias por usar esta aplicación de simulación y análisis!**")
