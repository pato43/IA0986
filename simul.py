import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO

# Configuración inicial de la aplicación
st.set_page_config(page_title="Dashboard de Presupuestos", layout="wide")

# Título del Dashboard
st.title("Control de Presupuestos 2021")

# Subida del archivo Excel
st.sidebar.header("Subir archivo Excel")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

# Verificación y carga del archivo Excel
def cargar_datos(file):
    try:
        data = pd.ExcelFile(file)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Limpieza del DataFrame
def limpiar_datos(df):
    df_cleaned = df.copy()

    # Convertir tipos de datos
    df_cleaned = df_cleaned.convert_dtypes()

    # Rellenar valores nulos
    df_cleaned = df_cleaned.fillna("N/A")

    # Forzar columnas de texto si son de tipo mixto
    for col in df_cleaned.columns:
        if df_cleaned[col].dtype == "object":
            df_cleaned[col] = df_cleaned[col].astype(str)

    return df_cleaned

# Mostrar las hojas disponibles y seleccionar
if uploaded_file:
    excel_data = cargar_datos(uploaded_file)
    if excel_data:
        st.sidebar.header("Seleccionar hoja de Excel")
        sheet_names = excel_data.sheet_names
        selected_sheet = st.sidebar.selectbox("Selecciona una hoja", sheet_names)

        # Cargar datos de la hoja seleccionada
        try:
            data = excel_data.parse(selected_sheet)
            st.success(f"Datos cargados correctamente desde la hoja: {selected_sheet}")

            # Mostrar datos iniciales
            st.write("Vista previa de los datos (primeras 10 filas):")
            data_cleaned = limpiar_datos(data)
            st.dataframe(data_cleaned.head(10))

        except Exception as e:
            st.error(f"Error al procesar los datos de la hoja: {e}")

    else:
        st.error("No se pudo procesar el archivo Excel.")
else:
    st.info("Sube un archivo Excel para comenzar.")
# 1. Introducción de filtros interactivos para explorar los datos
st.sidebar.header("Opciones de Filtro")

# Validación previa de columnas antes de aplicar filtros
required_columns = ['Departamento', 'Presupuesto', 'Gasto Real', 'Desviación', 'Observaciones']
if not all(col in data_cleaned.columns for col in required_columns):
    st.error(f"El archivo no contiene todas las columnas necesarias: {required_columns}")
else:
    unique_departments = data_cleaned['Departamento'].unique()
    department_filter = st.sidebar.multiselect(
        "Selecciona el departamento a visualizar:",
        options=unique_departments,
        default=unique_departments
    )

    filtered_data = data_cleaned[data_cleaned['Departamento'].isin(department_filter)]

    # 2. Muestra los datos filtrados
    st.subheader("Datos filtrados por Departamento")
    st.write(f"Total de filas después del filtro: {filtered_data.shape[0]}")
    st.dataframe(filtered_data)

    # 3. Gráfico de barras con visualizaciones agrupadas por departamento
    st.subheader("Distribución de Presupuesto por Departamento")
    fig, ax = plt.subplots(figsize=(10, 6))
    filtered_data.groupby('Departamento')['Presupuesto'].sum().sort_values(ascending=False).plot(kind='bar', ax=ax)
    ax.set_title("Total de Presupuesto por Departamento", fontsize=16)
    ax.set_ylabel("Presupuesto Total", fontsize=14)
    ax.set_xlabel("Departamento", fontsize=14)
    st.pyplot(fig)

    # 4. Gráfico de dispersión con Plotly
    st.subheader("Relación entre Presupuesto y Gasto Real")
    dispersions_chart = px.scatter(
        filtered_data,
        x='Presupuesto',
        y='Gasto Real',
        color='Departamento',
        size='Desviación',
        hover_data=['Desviación', 'Observaciones'],
        title="Presupuesto vs Gasto Real"
    )
    st.plotly_chart(dispersions_chart)

    # 5. Indicadores clásicos y KPIs
    st.sidebar.header("Indicadores Claves")

    total_budget = filtered_data['Presupuesto'].sum()
    total_expense = filtered_data['Gasto Real'].sum()
    total_difference = total_budget - total_expense
    total_deviation = filtered_data['Desviación'].sum()

    st.sidebar.metric("Presupuesto Total", f"${total_budget:,.2f}")
    st.sidebar.metric("Gasto Real Total", f"${total_expense:,.2f}")
    st.sidebar.metric("Diferencia Total", f"${total_difference:,.2f}")
    st.sidebar.metric("Desviación Acumulada", f"${total_deviation:,.2f}")

    # 6. Detección automática de anomalías en desviaciones
    st.subheader("Análisis de Anomalías")
    anomalies = filtered_data[
        filtered_data['Desviación'] > filtered_data['Desviación'].mean() + 2 * filtered_data['Desviación'].std()
    ]
    if anomalies.empty:
        st.write("No se detectaron desviaciones significativas.")
    else:
        st.write("Se detectaron las siguientes desviaciones significativas:")
        st.dataframe(anomalies)

    # 7. Notificaciones por correo para anomalías
    st.subheader("Notificaciones de Desviación")
    if st.button("Enviar notificaciones por correo"):
        import smtplib
        from email.mime.text import MIMEText

        recipients = ["rojasalexander10@gmail.com"]
        subject = "Alertas de Desviaciones en el Presupuesto"
        body = "Se detectaron las siguientes desviaciones:\n" + anomalies.to_string(index=False)

        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = "notificaciones@dashboard.com"
            msg['To'] = ", ".join(recipients)

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login("tu_correo@gmail.com", "tu_contraseña")
                server.sendmail("notificaciones@dashboard.com", recipients, msg.as_string())

            st.success("Las notificaciones se enviaron con éxito.")
        except Exception as e:
            st.error(f"Ocurrió un error al enviar las notificaciones: {e}")

    # 8. Opciones de exportación de datos
    st.subheader("Exportar Datos Filtrados")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, index=False, sheet_name='Datos Filtrados')
        writer.save()

    st.download_button(
        label="Descargar datos filtrados en Excel",
        data=buffer.getvalue(),
        file_name="datos_filtrados.xlsx",
        mime="application/vnd.ms-excel"
    )

    st.write("### Gracias por usar el dashboard interactivo.")
