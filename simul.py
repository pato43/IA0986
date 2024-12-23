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

# Menú principal
menu = st.sidebar.radio("Navegación", ["Vista Previa", "Estados", "Editar Datos", "Resumen y Reporte"])

# Ruta al archivo CSV
FILE_PATH = "cleaned_coti.csv"

@st.cache_data
def cargar_datos(file_path):
    datos = pd.read_csv(file_path)
    return datos

cotizaciones = cargar_datos(FILE_PATH)

if menu == "Vista Previa":
    # Mostrar los primeros registros para referencia
    st.subheader("Vista Previa de Datos")
    st.dataframe(cotizaciones.head(), use_container_width=True)

if menu == "Estados":
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
    st.dataframe(estados_resumen, use_container_width=True)

    # Gráfico de barras para estados
    def graficar_estados(datos):
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=datos, x="Estado", y="Cantidad", palette="viridis", ax=ax)
        ax.set_title("Distribución de Estados de Cotizaciones", fontsize=14)
        ax.set_ylabel("Cantidad", fontsize=12)
        ax.set_xlabel("Estado", fontsize=12)
        st.pyplot(fig)

    graficar_estados(estados_resumen)

if menu == "Editar Datos":
    # Sección para edición de datos relevantes
    st.subheader("Editar Datos Relevantes")
    st.write("Modifica los datos clave de las cotizaciones según sea necesario.")

    indice_seleccionado = st.selectbox("Selecciona una fila para editar:", cotizaciones.index)
    if indice_seleccionado is not None:
        with st.form(f"editar_fila_{indice_seleccionado}"):
            nuevo_monto = st.number_input("Monto", value=float(cotizaciones.at[indice_seleccionado, "Monto"]))
            nuevo_avance = st.slider("Avance (%)", 0, 100, int(cotizaciones.at[indice_seleccionado, "Avance_Porcentaje"]))
            nuevo_estado = asignar_estado(nuevo_avance)

            guardar_cambios = st.form_submit_button("Guardar Cambios")

            if guardar_cambios:
                cotizaciones.at[indice_seleccionado, "Monto"] = nuevo_monto
                cotizaciones.at[indice_seleccionado, "Avance_Porcentaje"] = nuevo_avance
                cotizaciones.at[indice_seleccionado, "Estado_Semaforo"] = nuevo_estado
                st.success("Datos actualizados correctamente.")

    # Descargar datos simplificados
    if st.button("Descargar Datos Simplificados"):
        datos_simplificados = cotizaciones[["Cliente", "Concepto", "Monto", "Avance_Porcentaje", "Estado_Semaforo"]]
        st.download_button(
            label="Descargar CSV",
            data=datos_simplificados.to_csv(index=False).encode("utf-8"),
            file_name="datos_simplificados.csv",
            mime="text/csv"
        )

if menu == "Resumen y Reporte":
    # Resumen general de cotizaciones
    st.subheader("Resumen General de Cotizaciones")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_cotizaciones = len(cotizaciones)
        st.metric("Total de Cotizaciones", total_cotizaciones)

    with col2:
        monto_total = cotizaciones["Monto"].sum()
        st.metric("Monto Total", f"${monto_total:,.2f}")

    with col3:
        avance_promedio = cotizaciones["Avance_Porcentaje"].mean()
        st.metric("Avance Promedio", f"{avance_promedio:.2f}%")

    # Simular envío de reporte por correo
    st.subheader("Enviar Reporte por Correo")
    correo = st.text_input("Ingresa el correo electrónico del destinatario")
    if st.button("Enviar Reporte"):
        if correo:
            st.success(f"Reporte enviado a {correo} (simulado).")
        else:
            st.error("Por favor, ingresa un correo válido.")
# Parte 2: Análisis Avanzado y Visualización de Pronósticos

# Sección: Cotizaciones 2020-2021
st.subheader("Análisis de Cotizaciones 2020-2021")

# Preparación de datos
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
def graficar_cotizaciones_anuales(datos):
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=datos, x="Año", y="Total_Monto", palette="crest", ax=ax)
    ax.set_title("Total de Monto por Año (2020-2021)", fontsize=14)
    ax.set_ylabel("Monto Total", fontsize=12)
    ax.set_xlabel("Año", fontsize=12)
    st.pyplot(fig)

graficar_cotizaciones_anuales(cotizaciones_anuales)

# Sección: Pronóstico de Ventas Mensuales
st.subheader("Pronóstico de Ventas Mensuales")

mes_actual = cotizaciones_fechas[pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.month == 12]
total_mes_actual = mes_actual["Monto"].sum()
st.metric(label="Ventas Estimadas para el Mes Actual", value=f"${total_mes_actual:,.2f}")

# Preparación de datos para series de tiempo
st.subheader("Pronóstico Anual de Ventas")
ventas_mensuales = cotizaciones_fechas.groupby(pd.to_datetime(cotizaciones_fechas["Fecha"], errors="coerce").dt.to_period("M")).agg(
    Total_Monto=("Monto", "sum")
).reset_index()
ventas_mensuales["Fecha"] = ventas_mensuales["Fecha"].dt.to_timestamp()

# Modelo de pronóstico simple
modelo = LinearRegression()
ventas_mensuales["Mes"] = np.arange(len(ventas_mensuales))
X = ventas_mensuales[["Mes"]]
y = ventas_mensuales["Total_Monto"]
modelo.fit(X, y)

# Predicciones futuras
meses_futuros = 12
nuevos_meses = np.arange(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros).reshape(-1, 1)
predicciones = modelo.predict(nuevos_meses)

# Combinar datos históricos y pronosticados
futuras_fechas = pd.date_range(ventas_mensuales["Fecha"].iloc[-1] + pd.DateOffset(months=1), periods=meses_futuros, freq="M")
datos_pronostico = pd.DataFrame({
    "Fecha": futuras_fechas,
    "Total_Monto": predicciones
})

ventas_completo = pd.concat([ventas_mensuales, datos_pronostico], ignore_index=True)
ventas_completo["Tipo"] = ["Histórico"] * len(ventas_mensuales) + ["Pronóstico"] * len(datos_pronostico)

# Gráfico de series de tiempo
def graficar_series(datos):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=datos, x="Fecha", y="Total_Monto", hue="Tipo", palette="tab10", ax=ax)
    ax.set_title("Pronóstico de Ventas Mensuales", fontsize=14)
    ax.set_ylabel("Monto Total", fontsize=12)
    ax.set_xlabel("Fecha", fontsize=12)
    st.pyplot(fig)

graficar_series(ventas_completo)

# Sección: Resumen General
st.subheader("Resumen Detallado de Pronósticos")
col1, col2, col3 = st.columns(3)

with col1:
    total_ventas_historicas = ventas_mensuales["Total_Monto"].sum()
    st.metric("Ventas Históricas Totales", f"${total_ventas_historicas:,.2f}")

with col2:
    total_ventas_pronosticadas = datos_pronostico["Total_Monto"].sum()
    st.metric("Ventas Pronosticadas Totales", f"${total_ventas_pronosticadas:,.2f}")

with col3:
    crecimiento_estimado = (total_ventas_pronosticadas / total_ventas_historicas - 1) * 100
    st.metric("Crecimiento Estimado (%)", f"{crecimiento_estimado:.2f}%")
# Parte 3: Interacción Avanzada y Exportación de Reportes

# Sección: Filtros Dinámicos
st.subheader("Filtros Dinámicos de Cotizaciones")
st.write("Utiliza los filtros para refinar las cotizaciones y obtener información específica.")

# Filtros
col1, col2, col3, col4 = st.columns(4)

with col1:
    filtro_area = st.selectbox("Filtrar por Área", ["Todos"] + cotizaciones["Area"].unique().tolist())
with col2:
    filtro_cliente = st.text_input("Buscar por Cliente")
with col3:
    filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "🟢 Aprobada", "🟡 Pendiente", "🔴 Rechazada"])
with col4:
    filtro_monto = st.slider("Filtrar por Monto", 0, int(cotizaciones["Monto"].max()), (0, int(cotizaciones["Monto"].max())))

# Aplicación de filtros
datos_filtrados = cotizaciones.copy()

if filtro_area != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Area"] == filtro_area]
if filtro_cliente:
    datos_filtrados = datos_filtrados[datos_filtrados["Cliente"].str.contains(filtro_cliente, case=False, na=False)]
if filtro_estado != "Todos":
    datos_filtrados = datos_filtrados[datos_filtrados["Estado_Semaforo"] == filtro_estado]
datos_filtrados = datos_filtrados[(datos_filtrados["Monto"] >= filtro_monto[0]) & (datos_filtrados["Monto"] <= filtro_monto[1])]

# Visualización de datos filtrados
st.write("Resultados Filtrados:")
st.dataframe(datos_filtrados, use_container_width=True)

# Sección: Exportación de Reportes
st.subheader("Exportación de Reportes")

# Descargar datos filtrados
if not datos_filtrados.empty:
    csv_filtrado = datos_filtrados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar Datos Filtrados",
        data=csv_filtrado,
        file_name="cotizaciones_filtradas.csv",
        mime="text/csv"
    )
else:
    st.warning("No hay datos para exportar con los filtros actuales.")

# Generación de Reporte PDF (Simulado)
st.subheader("Generación de Reporte PDF")
st.write("Esta función generará un PDF basado en los datos filtrados.")
if st.button("Generar PDF (Simulado)"):
    st.success("Reporte PDF generado exitosamente (simulado).")

# Sección: Métricas y Conclusiones Finales
st.subheader("Métricas Finales y Conclusiones")

col1, col2, col3 = st.columns(3)

with col1:
    total_cotizaciones_final = len(datos_filtrados)
    st.metric("Total Cotizaciones Filtradas", total_cotizaciones_final)

with col2:
    monto_total_filtrado = datos_filtrados["Monto"].sum()
    st.metric("Monto Total Filtrado", f"${monto_total_filtrado:,.2f}")

with col3:
    avance_promedio_filtrado = datos_filtrados["Avance_Porcentaje"].mean()
    st.metric("Avance Promedio Filtrado (%)", f"{avance_promedio_filtrado:.2f}%" if not pd.isnull(avance_promedio_filtrado) else "N/A")

# Gráfico final: Distribución de Monto por Estado
st.subheader("Distribución de Monto por Estado Filtrado")
def graficar_distribucion_estado(datos):
    if not datos.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(
            data=datos.groupby("Estado_Semaforo").agg(Total_Monto=("Monto", "sum")).reset_index(),
            x="Estado_Semaforo",
            y="Total_Monto",
            palette="coolwarm",
            ax=ax
        )
        ax.set_title("Distribución de Monto por Estado", fontsize=14)
        ax.set_ylabel("Monto Total", fontsize=12)
        ax.set_xlabel("Estado", fontsize=12)
        st.pyplot(fig)
    else:
        st.warning("No hay datos disponibles para graficar.")

graficar_distribucion_estado(datos_filtrados)

st.write("---")
st.write("Gracias por utilizar el Dashboard de Cotizaciones. Optimiza tus procesos y toma mejores decisiones con estas herramientas avanzadas.")
