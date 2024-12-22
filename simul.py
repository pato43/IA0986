# Parte 1: Importaciones, carga de datos y limpieza inicial

# Importar librerías necesarias
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Configuración inicial de Streamlit
st.set_page_config(
    page_title="Dashboard de Control de Presupuestos 2021",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Dashboard Interactivo de Control de Presupuestos 2021")
st.markdown("### Análisis avanzado de presupuestos para la gestión de recursos.")

# Importar archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel con los datos de presupuestos", type=["xlsx"])

# Verificación de carga del archivo
if uploaded_file is not None:
    # Cargar todas las hojas del archivo Excel
    excel_data = pd.ExcelFile(uploaded_file)
    sheet_names = excel_data.sheet_names

    # Mostrar opciones de selección de hoja
    st.sidebar.header("Opciones de configuración")
    sheet_selected = st.sidebar.selectbox("Selecciona la hoja a analizar", sheet_names)

    # Cargar datos de la hoja seleccionada
    data_raw = pd.read_excel(uploaded_file, sheet_name=sheet_selected)

    # Mostrar vista previa inicial
    st.subheader(f"Vista previa de los datos: {sheet_selected}")
    st.write("Datos sin procesar:")
    st.dataframe(data_raw.head(10))

    # Limpieza inicial
    st.subheader("Limpieza de datos")

    # Permitir al usuario seleccionar la fila de encabezados
    header_row = st.slider(
        "Selecciona la fila que contiene los encabezados (0-indexada):",
        min_value=0, max_value=min(len(data_raw)-1, 10), value=2
    )

    # Reasignar encabezados y limpiar datos
    data_raw.columns = data_raw.iloc[header_row].values
    data_cleaned = data_raw.iloc[header_row+1:].reset_index(drop=True)

    # Eliminar columnas completamente vacías
    data_cleaned = data_cleaned.dropna(how='all', axis=1)

    # Eliminar filas completamente vacías
    data_cleaned = data_cleaned.dropna(how='all', axis=0)

    # Mostrar datos procesados
    st.write("Datos procesados:")
    st.dataframe(data_cleaned.head(10))

    # Guardar en el estado de sesión para futuras operaciones
    st.session_state["data"] = data_cleaned

    # Mostrar estadísticas básicas
    st.subheader("Estadísticas descriptivas de las columnas numéricas")
    st.write(data_cleaned.describe(include=[np.number]))

    # Filtrar columnas específicas para análisis
    st.sidebar.subheader("Filtrado de columnas")
    numeric_columns = data_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_columns = st.sidebar.multiselect(
        "Selecciona columnas numéricas para visualizar", numeric_columns
    )

    if selected_columns:
        st.write("Datos filtrados por las columnas seleccionadas:")
        st.dataframe(data_cleaned[selected_columns].head())

    # Función para manejar valores faltantes
    def handle_missing_data(df, strategy="mean"):
        """
        Rellena valores faltantes en las columnas numéricas utilizando una estrategia especificada.
        Estrategias soportadas: mean, median, mode.
        """
        if strategy == "mean":
            return df.fillna(df.mean(numeric_only=True))
        elif strategy == "median":
            return df.fillna(df.median(numeric_only=True))
        elif strategy == "mode":
            return df.fillna(df.mode().iloc[0])
        else:
            raise ValueError("Estrategia no soportada")

    # Manejar valores faltantes según selección del usuario
    st.sidebar.subheader("Manejo de valores faltantes")
    missing_strategy = st.sidebar.radio(
        "Selecciona la estrategia para rellenar valores faltantes:",
        ("mean", "median", "mode", "none")
    )

    if missing_strategy != "none":
        data_cleaned = handle_missing_data(data_cleaned, strategy=missing_strategy)
        st.write(f"Valores faltantes rellenados utilizando la estrategia: {missing_strategy}")
        st.dataframe(data_cleaned.head())

    # Guardar datos limpios finales
    st.session_state["data_cleaned"] = data_cleaned

    # Visualización inicial
    st.subheader("Visualización de distribuciones de datos")

    # Gráfico de distribución para columnas seleccionadas
    if selected_columns:
        for col in selected_columns:
            st.write(f"Distribución de la columna: {col}")
            fig, ax = plt.subplots()
            sns.histplot(data_cleaned[col].dropna(), kde=True, ax=ax, color="blue")
            st.pyplot(fig)

    # Botón para avanzar
    if st.button("Continuar a visualización avanzada"):
        st.write("Listo para avanzar a la parte de análisis y gráficos interactivos.")

else:
    st.warning("Por favor, sube un archivo Excel para comenzar.")
# ----- PARTE 2: Visualizaciones avanzadas y estadísticas dinámicas ----- #

# Sección de visualizaciones avanzadas
st.header("Visualizaciones avanzadas")

# Selector para elegir el tipo de visualización
visualization_type = st.selectbox(
    "Selecciona el tipo de gráfico que deseas visualizar:",
    ["Gráfico de líneas", "Gráfico de barras", "Gráfico de dispersión", "Mapa de calor"]
)

# Selector dinámico para elegir las columnas a graficar
st.sidebar.subheader("Opciones de gráfico")
x_axis = st.sidebar.selectbox("Selecciona la columna para el eje X:", data.columns)
y_axis = st.sidebar.selectbox("Selecciona la columna para el eje Y:", data.columns)

# Generación de gráficos en base a la selección del usuario
if visualization_type == "Gráfico de líneas":
    st.subheader("Gráfico de líneas")
    line_fig = px.line(data, x=x_axis, y=y_axis, title=f"{y_axis} en función de {x_axis}")
    st.plotly_chart(line_fig)

elif visualization_type == "Gráfico de barras":
    st.subheader("Gráfico de barras")
    bar_fig = px.bar(data, x=x_axis, y=y_axis, title=f"Distribución de {y_axis} por {x_axis}")
    st.plotly_chart(bar_fig)

elif visualization_type == "Gráfico de dispersión":
    st.subheader("Gráfico de dispersión")
    scatter_fig = px.scatter(data, x=x_axis, y=y_axis, title=f"Relación entre {x_axis} y {y_axis}")
    st.plotly_chart(scatter_fig)

elif visualization_type == "Mapa de calor":
    st.subheader("Mapa de calor de correlaciones")
    correlation_matrix = data.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
    st.pyplot(plt)

# Sección de análisis estadísticos
st.header("Análisis estadísticos")

# Resumen estadístico dinámico
st.subheader("Resumen de estadísticas descriptivas")
summary_stats = data.describe()
st.write(summary_stats)

# Identificar valores máximos y mínimos
st.subheader("Valores máximos y mínimos")
col_selected = st.selectbox("Selecciona una columna para analizar sus valores extremos:", data.columns)
if pd.api.types.is_numeric_dtype(data[col_selected]):
    max_value = data[col_selected].max()
    min_value = data[col_selected].min()
    st.metric(label=f"Máximo en {col_selected}", value=max_value)
    st.metric(label=f"Mínimo en {col_selected}", value=min_value)
else:
    st.warning("Por favor, selecciona una columna numérica.")

# Histogramas interactivos
st.subheader("Histograma")
hist_column = st.selectbox("Selecciona la columna para el histograma:", data.columns)
bins = st.slider("Número de intervalos (bins):", min_value=5, max_value=50, value=10)
if pd.api.types.is_numeric_dtype(data[hist_column]):
    fig, ax = plt.subplots()
    sns.histplot(data[hist_column], bins=bins, kde=True, color="skyblue", ax=ax)
    ax.set_title(f"Histograma de {hist_column}")
    st.pyplot(fig)
else:
    st.warning("Por favor, selecciona una columna numérica.")

# Boxplot para análisis de outliers
st.subheader("Análisis de outliers con Boxplot")
boxplot_column = st.selectbox("Selecciona la columna para el Boxplot:", data.columns)
if pd.api.types.is_numeric_dtype(data[boxplot_column]):
    fig, ax = plt.subplots()
    sns.boxplot(data[boxplot_column], color="lightgreen", ax=ax)
    ax.set_title(f"Boxplot de {boxplot_column}")
    st.pyplot(fig)
else:
    st.warning("Por favor, selecciona una columna numérica.")

# Sección interactiva de filtros dinámicos
st.header("Filtrado dinámico de datos")
st.write("Usa las opciones de abajo para filtrar los datos según tus criterios.")

# Filtros por columnas específicas
filter_column = st.selectbox("Selecciona una columna para filtrar:", data.columns)
if pd.api.types.is_numeric_dtype(data[filter_column]):
    min_val, max_val = st.slider(
        f"Selecciona el rango de valores para {filter_column}:",
        min_value=float(data[filter_column].min()),
        max_value=float(data[filter_column].max()),
        value=(float(data[filter_column].min()), float(data[filter_column].max()))
    )
    filtered_data = data[(data[filter_column] >= min_val) & (data[filter_column] <= max_val)]
    st.dataframe(filtered_data)
else:
    unique_values = data[filter_column].unique()
    selected_values = st.multiselect(f"Selecciona los valores de {filter_column}:", unique_values, default=unique_values)
    filtered_data = data[data[filter_column].isin(selected_values)]
    st.dataframe(filtered_data)

# Exportar datos filtrados
st.download_button(
    label="Descargar datos filtrados en CSV",
    data=filtered_data.to_csv(index=False).encode("utf-8"),
    file_name="datos_filtrados.csv",
    mime="text/csv"
)
# PARTE 3: INTEGRACIÓN DE NOTIFICACIONES Y DETECCIÓN DE ANOMALÍAS

# Función para detectar desviaciones en los presupuestos
def detectar_anomalias(data):
    """
    Detecta desviaciones significativas en los datos del presupuesto utilizando z-scores.
    Retorna un DataFrame con las anomalías detectadas.
    """
    from scipy.stats import zscore

    df_anomalias = data.copy()
    df_anomalias['z_score'] = zscore(df_anomalias['Monto'])
    df_anomalias['Es_anomalia'] = df_anomalias['z_score'].abs() > 3

    anomalias_detectadas = df_anomalias[df_anomalias['Es_anomalia']]
    return anomalias_detectadas

# Mostrar anomalías en la interfaz
st.header("Detección de Anomalías")
if st.button("Detectar Anomalías"):
    with st.spinner("Analizando datos..."):
        anomalias = detectar_anomalias(df)
        if not anomalias.empty:
            st.error("Se han detectado las siguientes anomalías:")
            st.dataframe(anomalias[['Fecha', 'Descripción', 'Monto', 'z_score']])
        else:
            st.success("No se detectaron anomalías en los datos.")
    st.divider()

# Enviar notificaciones por correo al detectar anomalías
def enviar_notificacion(anomalias):
    """
    Envía un correo electrónico con información sobre las anomalías detectadas.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Configuración del correo
    destinatario = "rojasalexander10@gmail.com"
    remitente = "tu_correo@gmail.com"
    asunto = "Notificación de Anomalías Detectadas en el Dashboard"

    # Crear cuerpo del correo
    cuerpo = f"""
    Hola,

    Se han detectado las siguientes anomalías en los datos:
    {anomalias.to_string(index=False)}

    Por favor, revise el dashboard para más detalles.

    Saludos,
    Equipo de Control Presupuestal
    """
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    # Configurar servidor de correo
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, "tu_contraseña")  # Sustituir con tu contraseña
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        st.success("Correo enviado correctamente.")
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")

# Botón para enviar notificación
if st.button("Enviar Notificación de Anomalías"):
    if 'anomalias' in locals() and not anomalias.empty:
        enviar_notificacion(anomalias)
    else:
        st.warning("No hay anomalías detectadas para notificar.")
st.divider()

# Exportar datos filtrados
st.header("Exportar Datos Filtrados")
if st.button("Exportar"):
    # Crear archivo CSV con los datos actuales
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar archivo CSV",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv",
    )
    st.success("Archivo CSV generado con éxito.")

# Sección de ayuda e instrucciones
st.sidebar.title("Ayuda e Instrucciones")
st.sidebar.info(
    """
    **¿Cómo usar este dashboard?**
    
    - Carga los datos del presupuesto en formato Excel.
    - Usa los filtros para explorar los datos.
    - Detecta anomalías y revisa las desviaciones.
    - Envía notificaciones cuando sea necesario.
    - Exporta los datos para su uso externo.
    
    **Contacto:** rojasalexander10@gmail.com
    """
)

st.success("¡El dashboard está listo para usarse!")
