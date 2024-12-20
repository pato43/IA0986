# Parte 1: Configuración inicial y visualización básica en Streamlit

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="Plataforma Holman Service",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal de la aplicación
st.title("Plataforma Digital Holman Service")
st.subheader("Gestión de Procesos: Levantamiento, Cotización y Seguimiento")

# Introducción para los usuarios
st.markdown("""
Esta plataforma está diseñada para ayudar en la gestión integral de proyectos, desde el levantamiento inicial hasta la entrega y seguimiento. 
Con un enfoque en la optimización, permite visualizar datos clave y tomar decisiones basadas en análisis detallados.
""")

# Simulación de datos iniciales para demostración
st.sidebar.header("Cargar Datos")
data_source = st.sidebar.selectbox(
    "Selecciona el origen de los datos",
    ("Datos simulados", "Subir archivo CSV")
)

if data_source == "Datos simulados":
    # Generación de datos simulados para mostrar cómo funcionará la plataforma
    np.random.seed(42)
    data = pd.DataFrame({
        "Fase": np.random.choice(
            ["Levantamiento", "Cotización", "Compra de materiales", "Ejecución", "Entrega"],
            size=100
        ),
        "Duración (días)": np.random.randint(1, 30, size=100),
        "Costo ($)": np.random.uniform(1000, 50000, size=100),
        "Estatus": np.random.choice(["Pendiente", "En Proceso", "Completado"], size=100)
    })
    st.write("Se están utilizando datos simulados para esta demostración:")
else:
    # Cargar datos desde un archivo CSV proporcionado por el usuario
    uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.success("Datos cargados correctamente")
    else:
        st.warning("Por favor, sube un archivo CSV para continuar.")
        data = pd.DataFrame()  # Evitar errores si no hay datos

# Mostrar los datos cargados
if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("No hay datos para mostrar.")

# Visualización inicial: Distribución de las fases
if not data.empty:
    st.subheader("Distribución de las Fases del Proyecto")
    phase_counts = data["Fase"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=phase_counts.index, y=phase_counts.values, palette="viridis", ax=ax)
    ax.set_title("Número de Actividades por Fase")
    ax.set_ylabel("Número de Actividades")
    ax.set_xlabel("Fase")
    st.pyplot(fig)

# Sección adicional: Filtrado interactivo en la barra lateral
st.sidebar.header("Filtros")
fase_filtrada = st.sidebar.multiselect(
    "Selecciona las fases a visualizar",
    options=data["Fase"].unique() if not data.empty else [],
    default=data["Fase"].unique() if not data.empty else []
)

if fase_filtrada and not data.empty:
    data_filtrada = data[data["Fase"].isin(fase_filtrada)]
    st.subheader("Datos Filtrados")
    st.dataframe(data_filtrada)
else:
    st.warning("Selecciona al menos una fase para mostrar los datos filtrados.")

# Nota final en esta sección
st.info("Recuerda: Esta es solo la primera sección de la plataforma. ¡Pronto más funcionalidades!")
# Parte 2: Análisis avanzado y cronograma interactivo en Streamlit

# Análisis de costos totales por fase
if not data.empty:
    st.subheader("Análisis de Costos por Fase")
    cost_analysis = data.groupby("Fase")["Costo ($)"].sum().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=cost_analysis.index, y=cost_analysis.values, palette="coolwarm", ax=ax)
    ax.set_title("Costo Total por Fase")
    ax.set_ylabel("Costo Total ($)")
    ax.set_xlabel("Fase")
    st.pyplot(fig)
else:
    st.warning("No hay datos para realizar el análisis de costos.")

# Cronograma interactivo por duración
if not data.empty:
    st.subheader("Cronograma de Duración por Fase")
    gantt_data = data.copy()
    gantt_data["Inicio"] = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        np.cumsum(gantt_data["Duración (días)"].shift(fill_value=0)), unit="D"
    )
    gantt_data["Fin"] = gantt_data["Inicio"] + pd.to_timedelta(gantt_data["Duración (días)"], unit="D")
    
    # Crear un gráfico de Gantt
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, row in gantt_data.iterrows():
        ax.barh(row["Fase"], row["Duración (días)"], left=row["Inicio"].toordinal(), color="teal")
    ax.set_xlabel("Fecha")
    ax.set_title("Cronograma de Duración por Fase")
    st.pyplot(fig)
else:
    st.warning("No hay datos para generar el cronograma interactivo.")

# Análisis interactivo de costos y duración
st.sidebar.header("Análisis Comparativo")
analisis_seleccion = st.sidebar.selectbox(
    "Selecciona el análisis a realizar:",
    ("Duración vs. Costos", "Distribución de Estatus", "Análisis de Outliers")
)

if not data.empty:
    if analisis_seleccion == "Duración vs. Costos":
        st.subheader("Relación entre Duración y Costos")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            x="Duración (días)", 
            y="Costo ($)", 
            hue="Fase", 
            size="Costo ($)",
            sizes=(20, 200),
            data=data,
            palette="viridis",
            ax=ax
        )
        ax.set_title("Duración vs. Costos")
        st.pyplot(fig)
    elif analisis_seleccion == "Distribución de Estatus":
        st.subheader("Distribución de Estatus")
        status_counts = data["Estatus"].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=status_counts.index, y=status_counts.values, palette="pastel", ax=ax)
        ax.set_title("Distribución de Estatus")
        ax.set_ylabel("Cantidad")
        ax.set_xlabel("Estatus")
        st.pyplot(fig)
    elif analisis_seleccion == "Análisis de Outliers":
        st.subheader("Análisis de Outliers en Costos")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.boxplot(data=data, x="Fase", y="Costo ($)", palette="Set3", ax=ax)
        ax.set_title("Outliers en Costos por Fase")
        st.pyplot(fig)
else:
    st.warning("No hay datos para realizar el análisis comparativo.")

# Visualización de tendencias acumulativas
if not data.empty:
    st.subheader("Tendencia Acumulativa de Costos")
    trend_data = data.groupby("Fase").agg(
        {"Costo ($)": "sum", "Duración (días)": "sum"}
    ).cumsum()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=trend_data, markers=True, ax=ax)
    ax.set_title("Tendencia Acumulativa de Costos y Duración")
    ax.set_ylabel("Valores Acumulativos")
    ax.set_xlabel("Fase")
    st.pyplot(fig)
else:
    st.warning("No hay datos para mostrar tendencias acumulativas.")

# Adición de descargas personalizadas
st.sidebar.header("Opciones de Descarga")
descargar = st.sidebar.checkbox("Habilitar descarga de datos")
if descargar:
    csv = data.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="Descargar datos en CSV",
        data=csv,
        file_name="datos_proyecto.csv",
        mime="text/csv"
    )
    st.success("Descarga habilitada correctamente.")
else:
    st.sidebar.info("Habilita la descarga desde esta sección.")
# Parte 3: Optimización, Simulación y Análisis Predictivo

# Optimización de recursos y simulación de costos
if not data.empty:
    st.subheader("Optimización de Recursos y Simulación")
    
    # Parámetros de simulación
    st.sidebar.header("Parámetros de Simulación")
    incremento_costos = st.sidebar.slider(
        "Incremento esperado en costos (%)", min_value=0, max_value=50, value=10, step=5
    )
    reducción_duración = st.sidebar.slider(
        "Reducción esperada en duración (%)", min_value=0, max_value=30, value=5, step=5
    )
    
    # Simulación de nuevos valores
    data_simulada = data.copy()
    data_simulada["Costo Simulado ($)"] = data_simulada["Costo ($)"] * (1 + incremento_costos / 100)
    data_simulada["Duración Simulada (días)"] = data_simulada["Duración (días)"] * (1 - reducción_duración / 100)
    
    st.write("Datos Simulados:")
    st.dataframe(data_simulada)
    
    # Gráfico de comparación
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    sns.barplot(
        x="Fase", y="Costo Simulado ($)", data=data_simulada, palette="cool", ax=ax[0]
    )
    ax[0].set_title("Costos Simulados por Fase")
    ax[0].set_ylabel("Costo Simulado ($)")
    ax[0].set_xlabel("Fase")
    
    sns.barplot(
        x="Fase", y="Duración Simulada (días)", data=data_simulada, palette="Blues", ax=ax[1]
    )
    ax[1].set_title("Duración Simulada por Fase")
    ax[1].set_ylabel("Duración Simulada (días)")
    ax[1].set_xlabel("Fase")
    
    st.pyplot(fig)
else:
    st.warning("No hay datos para realizar simulaciones de costos y duración.")

# Modelo de Machine Learning para predicción de costos
if not data.empty:
    st.subheader("Predicción de Costos con Machine Learning")
    
    # Preparación de datos para el modelo
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    
    features = ["Duración (días)", "Fase_codificada"]
    data["Fase_codificada"] = data["Fase"].astype("category").cat.codes
    X = data[features]
    y = data["Costo ($)"]
    
    # División en datos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenamiento del modelo
    modelo = RandomForestRegressor(random_state=42)
    modelo.fit(X_train, y_train)
    
    # Predicción y evaluación
    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    st.write(f"**Error Absoluto Medio (MAE):** {mae:.2f}")
    st.write(f"**R² Score:** {r2:.2f}")
    
    # Predicción interactiva
    st.sidebar.header("Predicción Interactiva")
    input_duración = st.sidebar.slider(
        "Duración estimada (días)", min_value=1, max_value=365, value=30
    )
    input_fase = st.sidebar.selectbox(
        "Fase del proyecto", data["Fase"].unique()
    )
    fase_codificada = data.loc[data["Fase"] == input_fase, "Fase_codificada"].values[0]
    
    # Realizar predicción con los inputs
    nueva_predicción = modelo.predict([[input_duración, fase_codificada]])[0]
    st.write(f"**Predicción de Costo:** ${nueva_predicción:.2f}")
else:
    st.warning("No hay suficientes datos para entrenar el modelo de Machine Learning.")

# Exportación del modelo entrenado
st.sidebar.header("Exportar Modelo")
exportar_modelo = st.sidebar.checkbox("Habilitar exportación del modelo")
if exportar_modelo:
    import pickle
    modelo_serializado = pickle.dumps(modelo)
    st.sidebar.download_button(
        label="Descargar modelo entrenado",
        data=modelo_serializado,
        file_name="modelo_predicción.pkl",
        mime="application/octet-stream"
    )
    st.success("Modelo exportado correctamente.")
else:
    st.sidebar.info("Habilita la exportación del modelo desde esta sección.")

# Conclusión
st.subheader("Resumen Final")
st.write("""
Este proyecto permite:
- Analizar costos y tiempos detalladamente.
- Simular escenarios futuros con parámetros personalizables.
- Implementar un modelo de Machine Learning para predicciones de costos.
- Exportar datos y modelos para aplicaciones futuras.
""")
st.balloons()
