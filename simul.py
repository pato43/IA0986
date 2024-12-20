# Parte 1: Configuración inicial y visualización básica

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Detección de Anomalías",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("📊 Dashboard de Detección de Anomalías en Gastos e Inventarios")
st.markdown("""
Bienvenido al sistema interactivo para la detección de procesos irregulares en datos de gastos e inventarios.
Utiliza filtros dinámicos, gráficos avanzados y alertas para identificar posibles desviaciones.
""")

# Carga de datos simulados
@st.cache
def cargar_datos():
    np.random.seed(42)
    fechas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    datos = pd.DataFrame({
        "Fecha": fechas,
        "Categoría": np.random.choice(["Inventario", "Marketing", "Operaciones", "Otros"], size=len(fechas)),
        "Monto": np.random.normal(50000, 15000, size=len(fechas)).clip(min=0),
        "ID_Transacción": [f"T-{i}" for i in range(len(fechas))]
    })
    return datos

# Llamada a la función para cargar los datos
df = cargar_datos()

# Visualización inicial de los datos cargados
st.sidebar.header("Filtros")
st.sidebar.markdown("Ajusta los parámetros para analizar los datos.")

# Filtros interactivos
categorias = st.sidebar.multiselect(
    "Selecciona Categorías:",
    options=df["Categoría"].unique(),
    default=df["Categoría"].unique()
)

rango_montos = st.sidebar.slider(
    "Rango de Monto:",
    min_value=int(df["Monto"].min()),
    max_value=int(df["Monto"].max()),
    value=(int(df["Monto"].min()), int(df["Monto"].max()))
)

rango_fechas = st.sidebar.date_input(
    "Selecciona Rango de Fechas:",
    [df["Fecha"].min(), df["Fecha"].max()]
)

# Filtrado de los datos según los parámetros seleccionados
df_filtrado = df[
    (df["Categoría"].isin(categorias)) &
    (df["Monto"].between(rango_montos[0], rango_montos[1])) &
    (df["Fecha"].between(rango_fechas[0], rango_fechas[1]))
]

# Mostrar datos filtrados
st.write("### Datos Filtrados")
st.dataframe(df_filtrado)

# Métricas clave
st.write("### Resumen de Métricas Clave")
col1, col2, col3 = st.columns(3)

with col1:
    total_transacciones = len(df_filtrado)
    st.metric("Total de Transacciones", total_transacciones)

with col2:
    total_monto = df_filtrado["Monto"].sum()
    st.metric("Monto Total Filtrado", f"${total_monto:,.2f}")

with col3:
    promedio_monto = df_filtrado["Monto"].mean()
    st.metric("Monto Promedio", f"${promedio_monto:,.2f}")

# Alertas básicas de anomalías
st.write("### Alertas de Anomalías")
umbral_alto = 100000  # Definimos un umbral alto para identificar valores extremos
anomalías = df_filtrado[df_filtrado["Monto"] > umbral_alto]

if not anomalías.empty:
    st.warning(f"⚠️ Se han detectado {len(anomalías)} transacciones sospechosas con montos superiores a ${umbral_alto}.")
    st.dataframe(anomalías)
else:
    st.success("✅ No se detectaron transacciones sospechosas según el umbral definido.")

# Gráfico de montos por categoría
st.write("### Gráfico de Montos por Categoría")
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=df_filtrado, x="Categoría", y="Monto", ax=ax, palette="viridis")
ax.set_title("Distribución de Montos por Categoría")
ax.set_xlabel("Categoría")
ax.set_ylabel("Monto")
st.pyplot(fig)
# Parte 2: Visualización avanzada y análisis de anomalías

# Gráfico de tendencias por categoría
st.write("### Tendencias de Gastos por Categoría a lo Largo del Tiempo")
fig, ax = plt.subplots(figsize=(12, 6))
for categoria in df_filtrado["Categoría"].unique():
    datos_categoria = df_filtrado[df_filtrado["Categoría"] == categoria]
    ax.plot(datos_categoria["Fecha"], datos_categoria["Monto"].rolling(window=7).mean(), label=categoria)
ax.set_title("Tendencias de Gastos (Media Móvil de 7 Días)")
ax.set_xlabel("Fecha")
ax.set_ylabel("Monto Promedio")
ax.legend(title="Categoría")
st.pyplot(fig)

# Detección de anomalías por desviación estándar
st.write("### Análisis de Anomalías Avanzadas")
desviacion = df_filtrado["Monto"].std()
media = df_filtrado["Monto"].mean()
limite_superior = media + 3 * desviacion
limite_inferior = max(media - 3 * desviacion, 0)  # Evitar montos negativos

st.markdown(f"""
- **Límite Superior de Anomalías**: ${limite_superior:,.2f}  
- **Límite Inferior de Anomalías**: ${limite_inferior:,.2f}
""")

df_anomalías = df_filtrado[
    (df_filtrado["Monto"] > limite_superior) | (df_filtrado["Monto"] < limite_inferior)
]

if not df_anomalías.empty:
    st.warning(f"⚠️ Se detectaron {len(df_anomalías)} transacciones fuera del rango esperado.")
    st.dataframe(df_anomalías)
else:
    st.success("✅ No se detectaron anomalías en los datos filtrados según los límites calculados.")

# Gráfico de anomalías resaltadas
st.write("### Visualización de Anomalías Detectadas")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_filtrado["Fecha"], df_filtrado["Monto"], label="Monto")
ax.axhline(limite_superior, color="red", linestyle="--", label="Límite Superior")
ax.axhline(limite_inferior, color="blue", linestyle="--", label="Límite Inferior")
if not df_anomalías.empty:
    anomalías_fechas = df_anomalías["Fecha"]
    anomalías_montos = df_anomalías["Monto"]
    ax.scatter(anomalías_fechas, anomalías_montos, color="orange", label="Anomalías Detectadas")
ax.set_title("Anomalías en Gastos a lo Largo del Tiempo")
ax.set_xlabel("Fecha")
ax.set_ylabel("Monto")
ax.legend()
st.pyplot(fig)

# Histograma de distribución de montos
st.write("### Distribución de Montos")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df_filtrado["Monto"], bins=30, kde=True, color="green", ax=ax)
ax.axvline(media, color="red", linestyle="--", label="Media")
ax.axvline(limite_superior, color="orange", linestyle="--", label="Límite Superior (Anomalías)")
ax.axvline(limite_inferior, color="blue", linestyle="--", label="Límite Inferior (Anomalías)")
ax.set_title("Distribución de Montos con Límites de Anomalías")
ax.set_xlabel("Monto")
ax.set_ylabel("Frecuencia")
ax.legend()
st.pyplot(fig)

# Tabla de resumen estadístico
st.write("### Resumen Estadístico de Datos Filtrados")
resumen_estadistico = df_filtrado[["Monto"]].describe().T
resumen_estadistico["Varianza"] = df_filtrado["Monto"].var()
resumen_estadistico["Desviación Estándar"] = df_filtrado["Monto"].std()
st.table(resumen_estadistico)

# Proporción de anomalías por categoría
st.write("### Proporción de Anomalías por Categoría")
if not df_anomalías.empty:
    proporciones = df_anomalías["Categoría"].value_counts(normalize=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    proporciones.plot.pie(autopct="%1.1f%%", startangle=90, ax=ax, colormap="viridis")
    ax.set_ylabel("")
    ax.set_title("Porcentaje de Anomalías por Categoría")
    st.pyplot(fig)
else:
    st.info("No hay anomalías para calcular proporciones por categoría.")
# Parte 3: Análisis interactivo y predicción básica

# Filtro interactivo por categoría y rango de fechas
st.write("### Filtro Interactivo por Categoría y Fechas")
categorias_unicas = df_filtrado["Categoría"].unique()
categorias_seleccionadas = st.multiselect("Selecciona las categorías a analizar:", options=categorias_unicas, default=categorias_unicas)
rango_fechas = st.date_input("Selecciona el rango de fechas:", [df_filtrado["Fecha"].min(), df_filtrado["Fecha"].max()])

df_interactivo = df_filtrado[
    (df_filtrado["Categoría"].isin(categorias_seleccionadas)) &
    (df_filtrado["Fecha"] >= pd.Timestamp(rango_fechas[0])) &
    (df_filtrado["Fecha"] <= pd.Timestamp(rango_fechas[1]))
]

st.write("### Datos Filtrados:")
st.dataframe(df_interactivo)

# Gráfico de caja (boxplot) para analizar distribución de montos por categoría
st.write("### Distribución de Montos por Categoría (Boxplot)")
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=df_interactivo, x="Categoría", y="Monto", ax=ax, palette="Set2")
ax.set_title("Distribución de Montos por Categoría")
ax.set_xlabel("Categoría")
ax.set_ylabel("Monto")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)

# Clustering de gastos por categoría (KMeans)
st.write("### Clustering de Gastos por Categoría")
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Preprocesamiento
scaler = StandardScaler()
datos_cluster = df_interactivo.groupby("Categoría")["Monto"].sum().reset_index()
datos_cluster["Monto Escalado"] = scaler.fit_transform(datos_cluster[["Monto"]])

# Aplicar KMeans
kmeans = KMeans(n_clusters=3, random_state=42)
datos_cluster["Cluster"] = kmeans.fit_predict(datos_cluster[["Monto Escalado"]])

# Mostrar resultados
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(data=datos_cluster, x="Categoría", y="Monto", hue="Cluster", dodge=False, palette="tab10", ax=ax)
ax.set_title("Clusters de Categorías Basados en Montos")
ax.set_xlabel("Categoría")
ax.set_ylabel("Monto Total")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)

# Predicción básica de gastos futuros usando Prophet
st.write("### Predicción de Gastos Futuros (Modelo Prophet)")
from prophet import Prophet

# Preparar datos para Prophet
df_prediccion = df_filtrado.groupby("Fecha").sum()["Monto"].reset_index()
df_prediccion.columns = ["ds", "y"]

modelo = Prophet()
modelo.fit(df_prediccion)

# Hacer predicción a futuro
futuro = modelo.make_future_dataframe(periods=30)  # 30 días adicionales
pronostico = modelo.predict(futuro)

# Gráfico de predicción
fig = modelo.plot(pronostico)
plt.title("Predicción de Gastos Futuros (30 Días)")
st.pyplot(fig)

# Descomposición de componentes del modelo Prophet
st.write("### Componentes de Predicción (Prophet)")
fig2 = modelo.plot_components(pronostico)
st.pyplot(fig2)

# Heatmap de correlaciones entre categorías y montos
st.write("### Heatmap de Correlaciones")
df_correlacion = pd.pivot_table(df_interactivo, values="Monto", index="Fecha", columns="Categoría", aggfunc="sum").fillna(0)
correlaciones = df_correlacion.corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlaciones, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("Mapa de Calor de Correlaciones entre Categorías")
st.pyplot(fig)

# Exportar datos interactivos filtrados
st.write("### Exportar Datos Filtrados")
csv_interactivo = df_interactivo.to_csv(index=False)
st.download_button("Descargar Datos Filtrados como CSV", csv_interactivo, file_name="datos_filtrados.csv", mime="text/csv")
