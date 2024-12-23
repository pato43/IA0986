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
    Este dashboard permite gestionar, analizar y pronosticar las cotizaciones de manera eficiente. 
    Organiza la información en tablas útiles, permite editar datos esenciales y visualizar gráficos interactivos. 
    """
)

# Lectura del archivo cleaned_coti.csv
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    datos = pd.read_csv(file_path)
    return datos

cotizaciones = cargar_datos(FILE_PATH)

# Validar las columnas y asegurarse de que los datos sean del tipo correcto
columnas_necesarias = ["Cliente", "Concepto", "Monto", "Avance_Porcentaje", "Estatus", "Fecha", "Area"]
datos_validados = cotizaciones[columnas_necesarias].copy()

def limpiar_y_convertir(df, columna, tipo):
    if tipo == "numerico":
        df[columna] = pd.to_numeric(df[columna], errors="coerce").fillna(0)
    elif tipo == "fecha":
        df[columna] = pd.to_datetime(df[columna], errors="coerce")
    elif tipo == "texto":
        df[columna] = df[columna].fillna("Desconocido")

# Limpiar y convertir datos necesarios
limpiar_y_convertir(datos_validados, "Monto", "numerico")
limpiar_y_convertir(datos_validados, "Avance_Porcentaje", "numerico")
limpiar_y_convertir(datos_validados, "Fecha", "fecha")
limpiar_y_convertir(datos_validados, "Cliente", "texto")
limpiar_y_convertir(datos_validados, "Area", "texto")
limpiar_y_convertir(datos_validados, "Estatus", "texto")

# Semáforo en la tabla
st.subheader("Estado de Cotizaciones (Semáforo)")
def asignar_estado(avance):
    if avance == 100:
        return "🟢 Aprobada"
    elif avance >= 50:
        return "🟡 Pendiente"
    else:
        return "🔴 Rechazada"

datos_validados["Semaforo"] = datos_validados["Avance_Porcentaje"].apply(asignar_estado)

# Tablas Divididas
st.subheader("Tablas Esenciales")

# Tabla 1: Resumen por cliente
st.markdown("### Resumen por Cliente")
tabla_cliente = datos_validados.groupby("Cliente").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Cliente", "count")
).reset_index()
st.dataframe(tabla_cliente, use_container_width=True)

# Tabla 2: Resumen por área
st.markdown("### Resumen por Área")
tabla_area = datos_validados.groupby("Area").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Area", "count")
).reset_index()
st.dataframe(tabla_area, use_container_width=True)

# Tabla 3: Resumen por estatus
st.markdown("### Resumen por Estatus")
tabla_estatus = datos_validados.groupby("Estatus").agg(
    Total_Monto=("Monto", "sum"),
    Promedio_Avance=("Avance_Porcentaje", "mean"),
    Total_Cotizaciones=("Estatus", "count")
).reset_index()
st.dataframe(tabla_estatus, use_container_width=True)

# Edición de Datos Esenciales
st.subheader("Editar Datos Esenciales")
columna_editar = st.selectbox("Selecciona una columna para editar:", ["Cliente", "Concepto", "Monto", "Avance_Porcentaje", "Estatus", "Area"])

if columna_editar in ["Monto", "Avance_Porcentaje"]:
    nuevo_valor = st.number_input(f"Nuevo valor para la columna {columna_editar}", min_value=0.0)
    if st.button("Actualizar valores"):
        datos_validados[columna_editar] = nuevo_valor
        st.success(f"Columna {columna_editar} actualizada correctamente.")
else:
    valores_unicos = datos_validados[columna_editar].unique()
    nuevo_valor = st.text_input(f"Nuevo valor para la columna {columna_editar}")
    valor_a_reemplazar = st.selectbox(f"Selecciona un valor a reemplazar en {columna_editar}", valores_unicos)
    if st.button("Actualizar valores"):
        datos_validados[columna_editar] = datos_validados[columna_editar].replace(valor_a_reemplazar, nuevo_valor)
        st.success(f"Columna {columna_editar} actualizada correctamente.")

# Layout Mejorado con Tabs
st.markdown("---")
st.markdown("## Navegación de Secciones")
menu_tabs = st.tabs(["Inicio", "Tablas Resumidas", "Edición de Datos"])

with menu_tabs[0]:
    st.write("Bienvenido al Dashboard de Cotizaciones. Utiliza las pestañas para navegar entre las secciones.")

with menu_tabs[1]:
    st.subheader("Tablas Resumidas")
    st.markdown("Consulta los resúmenes organizados por cliente, área y estatus.")
    st.dataframe(tabla_cliente, use_container_width=True)
    st.dataframe(tabla_area, use_container_width=True)
    st.dataframe(tabla_estatus, use_container_width=True)

with menu_tabs[2]:
    st.subheader("Edición de Datos Esenciales")
    st.write("Utiliza las herramientas interactivas para editar los datos más relevantes.")
# Continuación del Dashboard: Parte 2

# Gráficos de Pronóstico y Tendencias
st.subheader("Pronóstico y Análisis de Tendencias")

# Datos para series de tiempo
ventas_mensuales = datos_validados.groupby(pd.to_datetime(datos_validados["Fecha"], errors="coerce").dt.to_period("M")).agg(
    Total_Monto=("Monto", "sum")
).reset_index()
ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

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
    "Selecciona un estado para filtrar:", options=["Todos"] + list(datos_validados["Semaforo"].unique())
)

# Aplicar filtros
filtros = datos_validados.copy()
if cliente_seleccionado != "Todos":
    filtros = filtros[filtros["Cliente"] == cliente_seleccionado]
if estado_seleccionado != "Todos":
    filtros = filtros[filtros["Semaforo"] == estado_seleccionado]

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
    tabla_cliente.to_excel(writer, sheet_name="Resumen_Cliente", index=False)
    tabla_area.to_excel(writer, sheet_name="Resumen_Area", index=False)
    tabla_estado.to_excel(writer, sheet_name="Resumen_Estado", index=False)
    tabla_cruzada.to_excel(writer, sheet_name="Cruzada_Area_Cliente")
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
