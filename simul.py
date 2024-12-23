import streamlit as st
import pandas as pd
import plotly.express as px
import io
from pandas import ExcelWriter

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Cargar y procesar datos
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Limpieza y simulación de datos faltantes
    df_copia["Monto"] = pd.to_numeric(df_copia["Monto"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(100000)
    df_copia["Avance_Porcentaje"] = pd.to_numeric(df_copia["Avance_Porcentaje"], errors="coerce").fillna(50)
    df_copia["2020"] = pd.to_numeric(df_copia["2020"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(2000000)
    df_copia["2021"] = pd.to_numeric(df_copia["2021"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(3000000)
    df_copia["Estatus"] = df_copia["Estatus"].fillna("Desconocido")

    # Manejo de valores nulos en Cliente
    df_copia["Cliente"] = df_copia["Cliente"].fillna("Cliente_Desconocido")

    # Agregar semáforo dinámico
    df_copia["Semaforo"] = df_copia["Avance_Porcentaje"].apply(
        lambda x: "🟢 Aprobada" if x >= 75 else ("🟡 Pendiente" if x >= 50 else "🔴 Rechazada")
    )

    # Simular datos repetidos para flujo de trabajo
    df_copia["Metodo_Captura"] = df_copia["Cliente"].apply(
        lambda x: "Teléfono" if "A" in x else ("Correo" if "E" in x else "Internet")
    )

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Sección inicial: Tabla general con semáforo
st.title("Dashboard de Cotizaciones")
st.markdown("Este dashboard permite gestionar cotizaciones de manera eficiente, simulando datos donde sea necesario.")

st.subheader("Estado General de Clientes")
st.dataframe(cotizaciones["Cliente", "Monto", "Estatus", "Semaforo", "Metodo_Captura"], use_container_width=True)

# Gráfico: Distribución por método de captura
st.subheader("Distribución por Método de Captura")
fig_captura = px.bar(
    cotizaciones.groupby("Metodo_Captura").size().reset_index(name="Cantidad"),
    x="Metodo_Captura",
    y="Cantidad",
    color="Metodo_Captura",
    title="Métodos de Captura de Cotizaciones",
    labels={"Cantidad": "Cantidad de Cotizaciones", "Metodo_Captura": "Método de Captura"},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_captura.update_traces(textposition="outside")
fig_captura.update_layout(xaxis_title="Método", yaxis_title="Cantidad")
st.plotly_chart(fig_captura)

# Edición interactiva de datos
st.subheader("Edición de Datos de Clientes")
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["Cliente"].unique())
columna_a_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Estatus", "Metodo_Captura"])
nuevo_valor = st.text_input("Introduce el nuevo valor:")
if st.button("Aplicar Cambios"):
    cotizaciones.loc[cotizaciones["Cliente"] == cliente_a_editar, columna_a_editar] = nuevo_valor
    st.success("¡El cambio ha sido aplicado con éxito!")

# Pronóstico Anual Consolidado
st.subheader("Pronóstico Anual Consolidado")

if "2020" in cotizaciones.columns and "2021" in cotizaciones.columns:
    pronostico_anual = pd.DataFrame({
        "Año": ["2020", "2021"],
        "Monto": [
            cotizaciones["2020"].sum(),
            cotizaciones["2021"].sum()
        ]
    })
else:
    pronostico_anual = pd.DataFrame({
        "Año": ["2020", "2021"],
        "Monto": [2000000, 3000000]  # Valores simulados
    })

fig_pronostico_anual = px.line(
    pronostico_anual,
    x="Año",
    y="Monto",
    title="Pronóstico Anual Consolidado",
    labels={"Monto": "Monto Total", "Año": "Año"},
    markers=True
)
fig_pronostico_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total")
st.plotly_chart(fig_pronostico_anual)

# Exportar Datos Actualizados
st.subheader("Exportar Datos Actualizados")

output = io.BytesIO()
with ExcelWriter(output, engine="xlsxwriter") as writer:
    cotizaciones.to_excel(writer, sheet_name="Cotizaciones", index=False)
    pronostico_anual.to_excel(writer, sheet_name="Pronostico_Anual", index=False)
    writer.save()

output.seek(0)
st.download_button(
    label="Descargar Datos Actualizados",
    data=output,
    file_name="cotizaciones_actualizadas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.info("Reporte consolidado generado con éxito. Revisa las proyecciones y resúmenes para decisiones informadas.")
