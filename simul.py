import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📈",
    layout="wide"
)

# Título del dashboard con diseño mejorado
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 48px;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #7f8c8d;
        margin-top: -10px;
        margin-bottom: 40px;
    }
    </style>
    <h1 class="title">Dashboard de Cotizaciones</h1>
    <p class="subtitle">Optimiza la gestión de tus cotizaciones con análisis interactivo</p>
    """,
    unsafe_allow_html=True
)

# Menú de navegación
menu = st.sidebar.radio(
    "Navegación",
    ["Vista Previa", "Editar Datos", "Estados y Análisis"],
    index=0
)

# Ruta al archivo CSV
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    try:
        datos = pd.read_csv(file_path)
        if "Fecha" not in datos.columns:
            datos["Fecha"] = pd.to_datetime("2023-01-01")  # Agregar columna ficticia si falta
        return datos
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

cotizaciones = cargar_datos(FILE_PATH)

if menu == "Vista Previa":
    st.subheader("Vista Previa de Datos")
    if not cotizaciones.empty:
        st.dataframe(cotizaciones, use_container_width=True)
    else:
        st.warning("No se encontraron datos en el archivo.")

if menu == "Editar Datos":
    st.subheader("Editar Datos Importantes")
    if not cotizaciones.empty:
        indice_seleccionado = st.selectbox(
            "Selecciona una fila para editar:",
            cotizaciones.index
        )
        if indice_seleccionado is not None:
            with st.form(f"form_editar_{indice_seleccionado}"):
                nuevo_monto = st.number_input(
                    "Monto",
                    value=float(cotizaciones.at[indice_seleccionado, "Monto"])
                )
                nuevo_avance = st.slider(
                    "Porcentaje de Avance",
                    0,
                    100,
                    int(cotizaciones.at[indice_seleccionado, "Avance_Porcentaje"])
                )
                guardar = st.form_submit_button("Guardar Cambios")
                if guardar:
                    cotizaciones.at[indice_seleccionado, "Monto"] = nuevo_monto
                    cotizaciones.at[indice_seleccionado, "Avance_Porcentaje"] = nuevo_avance
                    st.success("Datos actualizados correctamente.")
    else:
        st.warning("No se encontraron datos para editar.")

if menu == "Estados y Análisis":
    st.subheader("Estados de Cotizaciones")
    if not cotizaciones.empty:
        def asignar_estado(avance):
            if avance == 100:
                return "🟢 Aprobada"
            elif avance >= 50:
                return "🟡 Pendiente"
            else:
                return "🔴 Rechazada"

        cotizaciones["Estado"] = cotizaciones["Avance_Porcentaje"].apply(asignar_estado)

        st.write("Distribución de Estados:")
        estados_resumen = cotizaciones["Estado"].value_counts().reset_index()
        estados_resumen.columns = ["Estado", "Cantidad"]

        fig = px.bar(
            estados_resumen,
            x="Estado",
            y="Cantidad",
            color="Estado",
            color_discrete_map={"🟢 Aprobada": "green", "🟡 Pendiente": "yellow", "🔴 Rechazada": "red"},
            title="Distribución de Estados de Cotizaciones"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Pronóstico de Ventas Mensuales")

        cotizaciones["Fecha"] = pd.to_datetime(cotizaciones["Fecha"], errors="coerce")
        ventas_mensuales = cotizaciones.groupby(
            pd.to_datetime(cotizaciones["Fecha"], errors="coerce").dt.to_period("M")
        ).agg(Total_Monto=("Monto", "sum")).reset_index()
        ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

        ventas_mensuales["Mes"] = range(len(ventas_mensuales))
        X = ventas_mensuales[["Mes"]]
        y = ventas_mensuales["Total_Monto"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        meses_futuros = 12
        nuevos_meses = pd.DataFrame({"Mes": range(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros)})
        predicciones = modelo.predict(nuevos_meses)

        futuras_fechas = pd.date_range(
            start=ventas_mensuales["Fecha"].iloc[-1] + pd.DateOffset(months=1),
            periods=meses_futuros,
            freq="M"
        )

        ventas_pronostico = pd.DataFrame({
            "Fecha": futuras_fechas,
            "Total_Monto": predicciones,
            "Tipo": "Pronóstico"
        })

        ventas_historico = ventas_mensuales.copy()
        ventas_historico["Tipo"] = "Histórico"

        ventas_completo = pd.concat([ventas_historico, ventas_pronostico])

        fig_pronostico = px.line(
            ventas_completo,
            x="Fecha",
            y="Total_Monto",
            color="Tipo",
            title="Pronóstico de Ventas Mensuales",
            labels={"Total_Monto": "Monto Total", "Fecha": "Fecha"},
            color_discrete_map={"Histórico": "blue", "Pronóstico": "orange"}
        )
        fig_pronostico.update_traces(mode="lines+markers")
        st.plotly_chart(fig_pronostico, use_container_width=True)
    else:
        st.warning("No se encontraron datos para analizar.")
# Parte 2: Análisis Avanzado y Pronósticos Interactivos

st.subheader("Análisis de Cotizaciones 2020-2021")

cotizaciones_fechas = cotizaciones.copy()
cotizaciones_fechas["Año"] = pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.year

datos_2020_2021 = cotizaciones_fechas[cotizaciones_fechas["Año"].isin([2020, 2021])]
cotizaciones_anuales = datos_2020_2021.groupby("Año").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum")
).reset_index()

st.write("Resumen de Cotizaciones por Año:")
st.dataframe(cotizaciones_anuales, use_container_width=True)

# Gráfico: Cotizaciones por Año
fig_anual = px.bar(
    cotizaciones_anuales,
    x="Año",
    y="Total_Monto",
    text="Total_Monto",
    title="Monto Total de Cotizaciones por Año (2020-2021)",
    labels={"Total_Monto": "Monto Total", "Año": "Año"},
    color="Año",
    color_discrete_sequence=px.colors.sequential.Viridis
)
fig_anual.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_anual.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
st.plotly_chart(fig_anual, use_container_width=True)

# Pronóstico de Ventas Mensuales
st.subheader("Pronóstico de Ventas Mensuales")

ventas_mensuales = cotizaciones_fechas.groupby(
    pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.to_period("M")
).agg(Total_Monto=("Monto", "sum")).reset_index()
ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

# Modelo de pronóstico
ventas_mensuales["Mes"] = range(len(ventas_mensuales))
X = ventas_mensuales[["Mes"]]
y = ventas_mensuales["Total_Monto"]

# Ajuste del modelo
modelo = LinearRegression()
modelo.fit(X, y)

# Predicciones futuras
meses_futuros = 12
nuevos_meses = pd.DataFrame({"Mes": range(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros)})
predicciones = modelo.predict(nuevos_meses)

# Preparar datos para el gráfico
futuras_fechas = pd.date_range(
    start=ventas_mensuales["Fecha"].iloc[-1] + pd.DateOffset(months=1),
    periods=meses_futuros,
    freq="M"
)

ventas_pronostico = pd.DataFrame({
    "Fecha": futuras_fechas,
    "Total_Monto": predicciones,
    "Tipo": "Pronóstico"
})

ventas_historico = ventas_mensuales.copy()
ventas_historico["Tipo"] = "Histórico"

ventas_completo = pd.concat([ventas_historico, ventas_pronostico])

# Gráfico: Pronóstico de Ventas Mensuales
fig_pronostico = px.line(
    ventas_completo,
    x="Fecha",
    y="Total_Monto",
    color="Tipo",
    title="Pronóstico de Ventas Mensuales",
    labels={"Total_Monto": "Monto Total", "Fecha": "Fecha"},
    color_discrete_map={"Histórico": "blue", "Pronóstico": "orange"}
)
fig_pronostico.update_traces(mode="lines+markers")
st.plotly_chart(fig_pronostico, use_container_width=True)

# Resumen de Pronósticos
st.subheader("Resumen Detallado de Pronósticos")
col1, col2, col3 = st.columns(3)

with col1:
    total_historico = ventas_historico["Total_Monto"].sum()
    st.metric("Ventas Históricas Totales", f"${total_historico:,.2f}")

with col2:
    total_pronostico = ventas_pronostico["Total_Monto"].sum()
    st.metric("Ventas Pronosticadas Totales", f"${total_pronostico:,.2f}")

with col3:
    crecimiento_estimado = (total_pronostico / total_historico - 1) * 100
    st.metric("Crecimiento Estimado (%)", f"{crecimiento_estimado:.2f}%")
# Parte 3: Filtros Dinámicos, Exportación y Métricas Finales

# Sección: Filtros Dinámicos
st.subheader("Filtros Dinámicos de Cotizaciones")
st.write("Refina las cotizaciones según diferentes criterios para análisis específico.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    filtro_area = st.selectbox("Filtrar por Área", ["Todos"] + cotizaciones["Area"].unique().tolist())
with col2:
    filtro_cliente = st.text_input("Buscar por Cliente")
with col3:
    filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "🟢 Aprobada", "🟡 Pendiente", "🔴 Rechazada"])
with col4:
    filtro_monto = st.slider(
        "Filtrar por Monto",
        min_value=0,
        max_value=int(cotizaciones["Monto"].max()),
        value=(0, int(cotizaciones["Monto"].max()))
    )

# Aplicación de Filtros
datos_filtrados = cotizaciones.copy()
if filtro_area != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Area"] == filtro_area]
if filtro_cliente:
    datos_filtrados = datos_filtrados[datos_filtrados["Cliente"].str.contains(filtro_cliente, case=False, na=False)]
if filtro_estado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Estado"] == filtro_estado]
datos_filtrados = datos_filtrados[
    (datos_filtrados["Monto"] >= filtro_monto[0]) & (datos_filtrados["Monto"] <= filtro_monto[1])
]

st.write("Resultados Filtrados:")
st.dataframe(datos_filtrados, use_container_width=True)

# Exportación de Datos
st.subheader("Exportar Datos Filtrados")
if not datos_filtrados.empty:
    csv_filtrado = datos_filtrados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar CSV Filtrado",
        data=csv_filtrado,
        file_name="cotizaciones_filtradas.csv",
        mime="text/csv"
    )
else:
    st.warning("No hay datos para exportar con los filtros actuales.")

# Gráfico Interactivo: Distribución de Montos por Estado
st.subheader("Distribución de Montos por Estado")
if not datos_filtrados.empty:
    distribucion_estado = datos_filtrados.groupby("Estado").agg(
        Total_Monto=("Monto", "sum")
    ).reset_index()

    fig_estado = px.bar(
        distribucion_estado,
        x="Estado",
        y="Total_Monto",
        color="Estado",
        title="Distribución de Montos por Estado",
        labels={"Total_Monto": "Monto Total", "Estado": "Estado"},
        color_discrete_map={"🟢 Aprobada": "green", "🟡 Pendiente": "yellow", "🔴 Rechazada": "red"}
    )
    st.plotly_chart(fig_estado, use_container_width=True)
else:
    st.warning("No hay datos suficientes para graficar.")

# Métricas Finales
st.subheader("Métricas Finales")
col1, col2, col3 = st.columns(3)

with col1:
    total_filtrado = len(datos_filtrados)
    st.metric("Total de Cotizaciones Filtradas", total_filtrado)

with col2:
    monto_total_filtrado = datos_filtrados["Monto"].sum()
    st.metric("Monto Total Filtrado", f"${monto_total_filtrado:,.2f}")

with col3:
    avance_promedio_filtrado = datos_filtrados["Avance_Porcentaje"].mean()
    st.metric(
        "Avance Promedio (%)",
        f"{avance_promedio_filtrado:.2f}%" if not pd.isnull(avance_promedio_filtrado) else "N/A"
    )

# Simulación de Reporte PDF
st.subheader("Generación de Reporte PDF")
st.write("Simula la generación de un reporte en formato PDF basado en los datos filtrados.")
if st.button("Generar PDF (Simulado)"):
    st.success("Reporte PDF generado exitosamente (simulado).")

st.write("---")
st.write("Gracias por utilizar el Dashboard de Cotizaciones. Continúa optimizando tus procesos y toma mejores decisiones.")
