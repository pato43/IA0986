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
st.title("Dashboard de Cotizaciones")
st.markdown(
    """
    Este dashboard organiza las cotizaciones para facilitar el análisis, pronóstico y toma de decisiones. 
    Utiliza las secciones a continuación para explorar y gestionar la información.
    """
)

# Lectura del archivo cleaned_coti.csv
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    datos = pd.read_csv(file_path)
    return datos

cotizaciones = cargar_datos(FILE_PATH)

# Validación y limpieza de columnas necesarias
columnas_necesarias = [
    "Area", "Cliente", "Monto", "Estatus", "Avance_Porcentaje", "2020", "2021", "Pronostico_Suavizado"
]
datos_validados = cotizaciones[[col for col in columnas_necesarias if col in cotizaciones.columns]].copy()

# Limpieza de datos
def limpiar_y_convertir(df, columna, tipo):
    if tipo == "numerico":
        df[columna] = pd.to_numeric(df[columna].replace({"$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    elif tipo == "texto":
        df[columna] = df[columna].fillna("Desconocido")
    elif tipo == "fecha":
        df[columna] = pd.to_datetime(df[columna], errors="coerce")

limpiar_y_convertir(datos_validados, "Monto", "numerico")
limpiar_y_convertir(datos_validados, "Avance_Porcentaje", "numerico")
limpiar_y_convertir(datos_validados, "Cliente", "texto")
limpiar_y_convertir(datos_validados, "Estatus", "texto")

# Layout Mejorado
menu = st.tabs(["Vista General", "Tablas Detalladas", "Edición y Filtros"])

# Vista General
with menu[0]:
    st.header("Vista General")

    # Resumen General
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cotizaciones", len(datos_validados))
    col2.metric("Monto Total", f"${datos_validados['Monto'].sum():,.2f}")
    promedio_avance = datos_validados['Avance_Porcentaje'].mean()
    col3.metric("Avance Promedio", f"{promedio_avance:.2f}%")

    # Gráfico General
    fig_general = px.pie(
        datos_validados,
        names="Estatus",
        values="Monto",
        title="Distribución de Montos por Estatus",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_general)

# Tablas Detalladas
with menu[1]:
    st.header("Tablas Detalladas")

    # Tabla 1: Resumen por Cliente
    st.subheader("Resumen por Cliente")
    tabla_cliente = datos_validados.groupby("Cliente").agg(
        Total_Monto=("Monto", "sum"),
        Promedio_Avance=("Avance_Porcentaje", "mean"),
        Total_Cotizaciones=("Cliente", "count")
    ).reset_index()
    st.dataframe(tabla_cliente, use_container_width=True)

    # Tabla 2: Resumen por Área
    st.subheader("Resumen por Área")
    tabla_area = datos_validados.groupby("Area").agg(
        Total_Monto=("Monto", "sum"),
        Promedio_Avance=("Avance_Porcentaje", "mean"),
        Total_Cotizaciones=("Area", "count")
    ).reset_index()
    st.dataframe(tabla_area, use_container_width=True)

    # Tabla 3: Resumen por Año
    st.subheader("Resumen por Año")
    tabla_anual = datos_validados[["2020", "2021"]].sum().reset_index()
    tabla_anual.columns = ["Año", "Monto"]
    st.dataframe(tabla_anual, use_container_width=True)

# Edición y Filtros
with menu[2]:
    st.header("Edición y Filtros")

    # Filtros Simples
    st.subheader("Filtros")
    cliente_filtrado = st.selectbox("Selecciona un cliente para filtrar:", ["Todos"] + list(datos_validados["Cliente"].unique()))
    estatus_filtrado = st.selectbox("Selecciona un estatus para filtrar:", ["Todos"] + list(datos_validados["Estatus"].unique()))

    datos_filtrados = datos_validados.copy()
    if cliente_filtrado != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Cliente"] == cliente_filtrado]
    if estatus_filtrado != "Todos":
        datos_filtrados = datos_filtrados[datos_filtrados["Estatus"] == estatus_filtrado]

    st.dataframe(datos_filtrados, use_container_width=True)

    # Edición Interactiva
    st.subheader("Edición de Datos")
    columna_editar = st.selectbox("Selecciona una columna para editar:", ["Monto", "Avance_Porcentaje", "Estatus"])

    if columna_editar == "Monto":
        nuevo_valor = st.number_input("Nuevo valor para Monto", min_value=0.0)
        if st.button("Aplicar Edición"):
            datos_filtrados[columna_editar] = nuevo_valor
            st.success("Valores actualizados correctamente.")

    elif columna_editar == "Estatus":
        valor_reemplazo = st.text_input("Nuevo valor para Estatus")
        if st.button("Aplicar Edición"):
            datos_filtrados[columna_editar] = valor_reemplazo
            st.success("Estatus actualizado correctamente.")
# Continuación del Dashboard: Parte 2

# Gráficos de Pronóstico y Tendencias
st.subheader("Pronóstico y Análisis de Tendencias")

# Datos para series de tiempo
ventas_mensuales = datos_validados.groupby(pd.to_datetime(datos_validados['2020'], errors='coerce').dt.to_period("M")).agg(
    Total_Monto=("Monto", "sum")
).reset_index()
ventas_mensuales['Fecha'] = ventas_mensuales['2020'].dt.to_timestamp()

# Validar datos antes de realizar gráficos
if ventas_mensuales.empty:
    st.warning("No hay datos suficientes para generar gráficos de pronóstico y tendencias.")
else:
    # Modelo de predicción simple
    from sklearn.linear_model import LinearRegression
    modelo = LinearRegression()
    ventas_mensuales["Mes"] = range(len(ventas_mensuales))
    X = ventas_mensuales[["Mes"]]
    y = ventas_mensuales["Total_Monto"]

    if len(X) > 1:  # Evitar errores si solo hay un punto de datos
        modelo.fit(X, y)

        # Predicción para los próximos 12 meses
        meses_futuros = 12
        nuevos_meses = range(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros)
        predicciones = modelo.predict([[m] for m in nuevos_meses])

        # Datos combinados (históricos + pronóstico)
        futuras_fechas = pd.date_range(ventas_mensuales["Fecha"].iloc[-1] + pd.DateOffset(months=1), periods=meses_futuros, freq="M")
        datos_pronostico = pd.DataFrame({
            "Fecha": futuras_fechas,
            "Total_Monto": predicciones,
            "Tipo": "Pronóstico"
        })

        ventas_mensuales["Tipo"] = "Histórico"
        datos_completos = pd.concat([ventas_mensuales, datos_pronostico], ignore_index=True)

        # Gráfico de series de tiempo
        fig = px.line(
            datos_completos,
            x="Fecha",
            y="Total_Monto",
            color="Tipo",
            title="Pronóstico y Tendencias de Ventas Mensuales",
            labels={"Total_Monto": "Monto Total", "Fecha": "Mes"}
        )
        st.plotly_chart(fig)

    else:
        st.warning("Se necesitan más puntos de datos para realizar un pronóstico.")

# Resumen del Pronóstico
st.subheader("Resumen del Pronóstico Anual")
if 'predicciones' in locals():
    promedio_pronostico = predicciones.mean()
    st.metric(label="Promedio Mensual Pronosticado", value=f"${promedio_pronostico:,.2f}")
else:
    st.warning("No se pudo calcular un pronóstico mensual.")

# Gráfico de Monto por Área
st.subheader("Distribución de Montos por Área")
tabla_area = datos_validados.groupby("Area").agg(
    Total_Monto=("Monto", "sum")
).reset_index()

if not tabla_area.empty:
    fig_area = px.bar(
        tabla_area,
        x="Area",
        y="Total_Monto",
        title="Distribución de Montos por Área",
        labels={"Total_Monto": "Monto Total", "Area": "Área"},
        text="Total_Monto",
        color="Area",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_area.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    st.plotly_chart(fig_area)
else:
    st.warning("No hay datos disponibles para graficar por área.")

# Exportación de datos procesados
st.subheader("Exportación de Datos Procesados")
st.download_button(
    label="Descargar Cotizaciones Actualizadas",
    data=datos_validados.to_csv(index=False).encode('utf-8'),
    file_name="cotizaciones_actualizadas.csv",
    mime="text/csv"
)

# Fin de la Parte 2
st.markdown("---")
st.info("Esta sección incluye el análisis de pronóstico y tendencias basado en los datos actuales.")
# Continuación del Dashboard: Parte 3

# Comparativa de Vendedores
st.subheader("Desempeño de Vendedores")

grafico_vendedores = datos_validados.groupby("Vendedor").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

if not grafico_vendedores.empty:
    fig_vendedores = px.bar(
        grafico_vendedores,
        x="Vendedor",
        y="Total_Monto",
        color="Promedio_Avance",
        title="Monto Total de Cotizaciones por Vendedor",
        labels={"Total_Monto": "Monto Total", "Vendedor": "Vendedor", "Promedio_Avance": "Avance Promedio"},
        text="Total_Monto",
        color_continuous_scale="Bluered"
    )
    fig_vendedores.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_vendedores.update_layout(xaxis_title="Vendedor", yaxis_title="Monto Total", xaxis_tickangle=-45)
    st.plotly_chart(fig_vendedores)
else:
    st.warning("No hay datos disponibles para graficar el desempeño por vendedor.")

# Evaluación por Clasificación
st.subheader("Desempeño por Clasificación de Clientes")

grafico_clasificacion = datos_validados.groupby("Clasificacion").agg(
    Total_Cotizaciones=("Monto", "count"),
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean")
).reset_index()

if not grafico_clasificacion.empty:
    fig_clasificacion = px.bar(
        grafico_clasificacion,
        x="Clasificacion",
        y="Total_Monto",
        color="Promedio_Avance",
        title="Monto Total por Clasificación de Clientes",
        labels={"Total_Monto": "Monto Total", "Clasificacion": "Clasificación", "Promedio_Avance": "Avance Promedio"},
        text="Total_Monto",
        color_continuous_scale="Viridis"
    )
    fig_clasificacion.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig_clasificacion.update_layout(xaxis_title="Clasificación", yaxis_title="Monto Total")
    st.plotly_chart(fig_clasificacion)
else:
    st.warning("No hay datos disponibles para graficar por clasificación de clientes.")

# Filtros Dinámicos para Cotizaciones
st.subheader("Explorar Cotizaciones con Filtros Dinámicos")

# Filtro por cliente
cliente_seleccionado = st.selectbox(
    "Selecciona un cliente para filtrar:", options=["Todos"] + list(datos_validados["Cliente"].unique())
)

# Filtro por estado de semáforo
estado_seleccionado = st.selectbox(
    "Selecciona un estado para filtrar:", options=["Todos"] + list(datos_validados["Estatus"].unique())
)

# Aplicar filtros
filtros = datos_validados.copy()
if cliente_seleccionado != "Todos":
    filtros = filtros[filtros["Cliente"] == cliente_seleccionado]
if estado_seleccionado != "Todos":
    filtros = filtros[filtros["Estatus"] == estado_seleccionado]

# Mostrar resultados filtrados
st.write("Resultados Filtrados:")
st.dataframe(filtros, use_container_width=True)

# Gráfico dinámico basado en filtros
if not filtros.empty:
    st.subheader("Distribución de Montos Filtrados")
    fig_filtros = px.histogram(
        filtros,
        x="Monto",
        nbins=15,
        title="Distribución de Montos Filtrados",
        labels={"Monto": "Monto"},
        color_discrete_sequence=["blue"]
    )
    fig_filtros.update_layout(xaxis_title="Monto", yaxis_title="Frecuencia")
    st.plotly_chart(fig_filtros)
else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")

# Exportación de Resultados Filtrados
st.subheader("Exportar Resultados Filtrados")
if not filtros.empty:
    st.download_button(
        label="Descargar Datos Filtrados",
        data=filtros.to_csv(index=False).encode("utf-8"),
        file_name="cotizaciones_filtradas.csv",
        mime="text/csv"
    )
else:
    st.warning("No hay datos disponibles para exportar.")

# Finalización de la Parte 3
st.markdown("---")
st.info("Concluimos con los análisis de clasificación, desempeño por vendedor y filtros dinámicos.")
# Continuación del Dashboard: Parte 4

# Análisis Dinámico por Área y Cliente
st.subheader("Análisis Avanzado por Área y Cliente")

# Crear una tabla cruzada entre Área y Cliente
tabla_cruzada = pd.pivot_table(
    datos_validados,
    values="Monto",
    index="Area",
    columns="Cliente",
    aggfunc="sum",
    fill_value=0
)

st.markdown("### Tabla Cruzada: Área vs Cliente")
st.dataframe(tabla_cruzada, use_container_width=True)

# Gráfico de Heatmap
st.markdown("### Heatmap de Montos por Área y Cliente")
fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=tabla_cruzada.values,
        x=tabla_cruzada.columns,
        y=tabla_cruzada.index,
        colorscale="Viridis",
        colorbar=dict(title="Monto Total")
    )
)
fig_heatmap.update_layout(
    title="Distribución de Montos por Área y Cliente",
    xaxis_title="Cliente",
    yaxis_title="Área"
)
st.plotly_chart(fig_heatmap)

# Análisis de Cotizaciones por Estado
st.subheader("Análisis de Cotizaciones por Estado")

# Crear una tabla resumida por estado
tabla_estado = datos_validados.groupby("Estatus").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Estatus", "count")
).reset_index()

# Mostrar tabla resumida
st.markdown("### Resumen por Estado")
st.dataframe(tabla_estado, use_container_width=True)

# Gráfico de Barras por Estado
st.markdown("### Gráfico de Barras por Estado")
fig_estado = px.bar(
    tabla_estado,
    x="Estatus",
    y="Total_Monto",
    title="Monto Total por Estado",
    labels={"Total_Monto": "Monto Total", "Estatus": "Estado"},
    text="Total_Monto",
    color="Estatus",
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_estado.update_traces(texttemplate="%{text:.2s}", textposition="outside")
fig_estado.update_layout(xaxis_title="Estado", yaxis_title="Monto Total")
st.plotly_chart(fig_estado)

# Reporte Consolidado
st.subheader("Generar Reporte Consolidado")

# Consolidar todas las tablas en un archivo Excel
import io
from pandas import ExcelWriter

output = io.BytesIO()
with ExcelWriter(output, engine="xlsxwriter") as writer:
    datos_validados.to_excel(writer, sheet_name="Cotizaciones", index=False)
    tabla_cruzada.to_excel(writer, sheet_name="Cruzada_Area_Cliente")
    tabla_estado.to_excel(writer, sheet_name="Resumen_Estado", index=False)
    writer.save()

output.seek(0)
st.download_button(
    label="Descargar Reporte Consolidado",
    data=output,
    file_name="reporte_cotizaciones.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Finalización
st.markdown("---")
st.info("Gracias por utilizar el Dashboard de Cotizaciones. Todas las funcionalidades han sido cubiertas.")
