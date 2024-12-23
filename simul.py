import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np

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
    Este dashboard permite gestionar, analizar y pronosticar las cotizaciones de manera eficiente. A continuación, 
    podrás visualizar datos clave, realizar ediciones y explorar tendencias de las cotizaciones.
    """
)

# Lectura del archivo cleaned_coti.csv
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    datos = pd.read_csv(file_path)
    return datos

cotizaciones = cargar_datos(FILE_PATH)

# Validar y convertir columnas relevantes
numericas = ["Monto", "Avance_Porcentaje"]
for col in numericas:
    cotizaciones[col] = pd.to_numeric(cotizaciones[col], errors="coerce")

# Mostrar los primeros registros para referencia
st.subheader("Vista Previa de Datos")
st.dataframe(cotizaciones.head(), use_container_width=True)

# Sección para edición de datos relevantes
st.subheader("Editar Datos Relevantes")
if st.checkbox("Habilitar edición de datos"):
    st.warning("Edite con cuidado, estos cambios afectan el archivo cargado.")
    for columna in cotizaciones.columns:
        if cotizaciones[columna].dtype == 'object':
            nuevos_valores = st.text_area(f"Editar valores para {columna}", ", ".join(cotizaciones[columna].dropna().unique()))
            if nuevos_valores:
                nuevos_valores = nuevos_valores.split(", ")
                cotizaciones[columna] = cotizaciones[columna].apply(lambda x: nuevos_valores[0] if x == nuevos_valores[1] else x)
        elif cotizaciones[columna].dtype in ['int64', 'float64']:
            min_val = st.number_input(f"Valor mínimo para {columna}", value=float(cotizaciones[columna].min()))
            max_val = st.number_input(f"Valor máximo para {columna}", value=float(cotizaciones[columna].max()))
            cotizaciones[columna] = cotizaciones[columna].clip(lower=min_val, upper=max_val)

    st.success("Ediciones aplicadas correctamente.")

# Determinación del estado del semáforo
st.subheader("Estados de Cotizaciones")
def asignar_estado(avance):
    if avance == 100:
        return "🟢 Aprobada"
    elif avance >= 50:
        return "🟡 Pendiente"
    else:
        return "🔴 Rechazada"

cotizaciones["Estado_Semaforo"] = cotizaciones["Avance_Porcentaje"].apply(asignar_estado)

# Tabla resumen por estado
st.write("Distribución de Estados de las Cotizaciones:")
estados_resumen = cotizaciones["Estado_Semaforo"].value_counts().reset_index()
estados_resumen.columns = ["Estado", "Cantidad"]
col1, col2 = st.columns([2, 1])
with col1:
    st.dataframe(estados_resumen, use_container_width=True)

# Gráfico de barras para estados
def graficar_estados(datos):
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=datos, x="Estado", y="Cantidad", palette="viridis", ax=ax)
    ax.set_title("Distribución de Estados de Cotizaciones", fontsize=14)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_xlabel("Estado", fontsize=12)
    st.pyplot(fig)

with col2:
    graficar_estados(estados_resumen)

# Datos de cotizaciones 2020-2021
st.subheader("Análisis de Cotizaciones 2020-2021")
cotizaciones_fechas = cotizaciones.copy()
cotizaciones_fechas["Año"] = pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.year

datos_2020_2021 = cotizaciones_fechas[cotizaciones_fechas["Año"].isin([2020, 2021])]
cotizaciones_anuales = datos_2020_2021.groupby("Año").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum")
).reset_index()

col3, col4 = st.columns([2, 1])
with col3:
    st.write("Resumen de Cotizaciones por Año:")
    st.dataframe(cotizaciones_anuales, use_container_width=True)

# Gráfico de barras para 2020-2021
def graficar_cotizaciones_anuales(datos):
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=datos, x="Año", y="Total_Monto", palette="crest", ax=ax)
    ax.set_title("Total de Monto por Año (2020-2021)", fontsize=14)
    ax.set_ylabel("Monto Total", fontsize=12)
    ax.set_xlabel("Año", fontsize=12)
    st.pyplot(fig)

with col4:
    graficar_cotizaciones_anuales(cotizaciones_anuales)

# Pronóstico de ventas mensuales
st.subheader("Pronóstico de Ventas Mensuales")
mes_actual = cotizaciones_fechas[pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.month == 12]
total_mes_actual = mes_actual["Monto"].sum()
st.metric(label="Ventas Estimadas para el Mes Actual", value=f"${total_mes_actual:,.2f}")
# Continuación del Dashboard: Parte 2

# Pronóstico Anual de Ventas
st.subheader("Pronóstico Anual de Ventas")

# Preparar datos de series de tiempo
ventas_mensuales = cotizaciones_fechas.groupby(pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.to_period("M")).agg(
    Total_Monto=("Monto", "sum")
).reset_index()
ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

# Crear modelo de regresión lineal para predicciones
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
    def graficar_series(datos):
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=datos, x="Fecha", y="Total_Monto", hue="Tipo", palette="tab10", ax=ax)
        ax.set_title("Pronóstico Anual de Ventas", fontsize=16)
        ax.set_ylabel("Monto Total", fontsize=12)
        ax.set_xlabel("Fecha", fontsize=12)
        ax.legend(title="Tipo de Datos")
        st.pyplot(fig)

    graficar_series(datos_completos)
else:
    st.warning("Los datos no son suficientes para generar un modelo de pronóstico.")

# Resumen de Pronóstico Anual
st.subheader("Resumen de Pronóstico Anual")
promedio_pronostico = predicciones.mean() if 'predicciones' in locals() else 0
st.metric(label="Promedio Pronosticado Mensual", value=f"${promedio_pronostico:,.2f}")

# Sección de Exportación
st.subheader("Exportar Datos Procesados")
if not cotizaciones.empty:
    st.download_button(
        label="Descargar Cotizaciones Actualizadas",
        data=cotizaciones.to_csv(index=False).encode('utf-8'),
        file_name="cotizaciones_actualizadas.csv",
        mime="text/csv"
    )

# Tablas dinámicas para análisis
st.subheader("Análisis Dinámico de Cotizaciones")
# Agrupación por cliente
st.markdown("#### Agrupación por Cliente")
tabla_cliente = cotizaciones.groupby("Cliente").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Cliente", "count")
).reset_index()
st.dataframe(tabla_cliente, use_container_width=True)

# Agrupación por estado
st.markdown("#### Agrupación por Estado de Semáforo")
tabla_estado = cotizaciones.groupby("Estado_Semaforo").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Estado_Semaforo", "count")
).reset_index()
st.dataframe(tabla_estado, use_container_width=True)

# Final de la parte 2
st.markdown("---")
st.info("Esta sección concluye el análisis de pronósticos y agrupaciones dinámicas de cotizaciones.")
# Continuación del Dashboard: Parte 3

# Gráficos avanzados e interactividad adicional

# Visualización de tendencias de cotización por área
st.subheader("Tendencias de Cotización por Área")

grafico_area = cotizaciones.groupby("Area").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum")
).reset_index()

def graficar_por_area(datos):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=datos, x="Area", y="Total_Monto", palette="coolwarm", ax=ax)
    ax.set_title("Monto Total de Cotizaciones por Área", fontsize=16)
    ax.set_ylabel("Monto Total", fontsize=12)
    ax.set_xlabel("Área", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

graficar_por_area(grafico_area)

# Comparativa entre vendedores
st.subheader("Comparativa de Vendedores")

grafico_vendedores = cotizaciones.groupby("Vendedor").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

def graficar_por_vendedor(datos):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=datos, x="Vendedor", y="Total_Monto", palette="magma", ax=ax)
    ax.set_title("Monto Total de Cotizaciones por Vendedor", fontsize=16)
    ax.set_ylabel("Monto Total", fontsize=12)
    ax.set_xlabel("Vendedor", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

graficar_por_vendedor(grafico_vendedores)

# Interacción con filtros dinámicos
st.subheader("Explorar Cotizaciones con Filtros Dinámicos")

# Filtro por cliente
cliente_seleccionado = st.selectbox(
    "Selecciona un cliente para filtrar:", options=["Todos"] + list(cotizaciones["Cliente"].unique())
)

# Filtro por estado de semáforo
estado_seleccionado = st.selectbox(
    "Selecciona un estado para filtrar:", options=["Todos"] + list(cotizaciones["Estado_Semaforo"].unique())
)

# Aplicar filtros
filtros = cotizaciones.copy()
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
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(filtros, x="Monto", bins=15, kde=True, color="blue", ax=ax)
    ax.set_title("Distribución de Montos Filtrados", fontsize=16)
    ax.set_xlabel("Monto", fontsize=12)
    ax.set_ylabel("Frecuencia", fontsize=12)
    st.pyplot(fig)
else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")

# Evaluación de desempeño por clasificación
st.subheader("Desempeño por Clasificación de Clientes")

grafico_clasificacion = cotizaciones.groupby("Clasificacion").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=grafico_clasificacion, x="Clasificacion", y="Total_Monto", palette="cubehelix", ax=ax)
ax.set_title("Monto Total por Clasificación", fontsize=16)
ax.set_xlabel("Clasificación", fontsize=12)
ax.set_ylabel("Monto Total", fontsize=12)
st.pyplot(fig)

# Sección final
st.markdown("---")
st.info("Has explorado todas las secciones avanzadas del dashboard. Ahora puedes tomar decisiones más informadas sobre las cotizaciones.")
