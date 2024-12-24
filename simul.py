import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Ruta del archivo CSV limpio
FILE_PATH = "cleaned_coti.csv"

# Función para cargar y procesar los datos
@st.cache_data
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Renombrar columnas para ajustarse a los nombres requeridos
    df_copia.rename(columns={
        "Monto": "MONTO",
        "Cliente": "CLIENTE",
        "Estatus": "ESTATUS",
        "Fecha_Envio": "FECHA ENVIO",
        "Duracion_Dias": "DIAS",
        "Metodo_Captura": "LLAMADA AL CLIENTE",
        "Concepto": "CONCEPTO"
    }, inplace=True)

    # Agregar columnas faltantes con valores por defecto
    df_copia["AREA"] = df_copia.get("AREA", "General")
    df_copia["CLASIFICACION"] = df_copia.get("CLASIFICACION", "No clasificado")
    df_copia["VENDEDOR"] = df_copia.get("VENDEDOR", "Desconocido")
    df_copia["Cotizado X CLIENTE"] = df_copia.get("Cotizado X CLIENTE", 0)
    df_copia["Comentarios"] = df_copia.get("Comentarios", "Sin comentarios")

    # Crear columna de semáforo basada en el estatus
    df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos
cotizaciones = cargar_datos(FILE_PATH)

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard permite gestionar cotizaciones de manera eficiente, con funcionalidad para edición de datos, 
comentarios, análisis y generación de reportes automatizados.
""")

# Tabla principal
st.subheader("Estado General de Clientes")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]
st.dataframe(cotizaciones[columnas_mostrar], use_container_width=True)

# Nueva sección: Tabla filtrable para presupuestos, montos y cotizaciones
st.subheader("Tabla Filtrable: Presupuestos, Montos y Cotizaciones")

# Filtros específicos
monto_min = st.number_input("Monto mínimo", min_value=0, value=0)
monto_max = st.number_input("Monto máximo", min_value=0, value=int(cotizaciones["MONTO"].max()))

cotizaciones_filtradas_tabla = cotizaciones[
    (cotizaciones["MONTO"] >= monto_min) & (cotizaciones["MONTO"] <= monto_max)
]

# Mostrar tabla filtrada
st.dataframe(cotizaciones_filtradas_tabla, use_container_width=True)

# Filtros interactivos
st.subheader("Filtrar por Estado del Semáforo")
semaforo_seleccionado = st.selectbox(
    "Selecciona el estado del semáforo:",
    ["Todos"] + cotizaciones["Semaforo"].unique().tolist()
)

if semaforo_seleccionado != "Todos":
    cotizaciones_filtradas = cotizaciones[cotizaciones["Semaforo"] == semaforo_seleccionado]
else:
    cotizaciones_filtradas = cotizaciones

st.dataframe(cotizaciones_filtradas[columnas_mostrar], use_container_width=True)

# Métricas principales
st.subheader("Métricas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones))
col2.metric("Monto Total", f"${cotizaciones['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones['DIAS'].mean():.2f}")

# Edición de datos interactiva
st.subheader("Edición de Datos")
cliente_a_editar = st.selectbox("Selecciona un cliente para editar:", cotizaciones["CLIENTE"].unique())
columna_a_editar = st.selectbox(
    "Selecciona una columna para editar:",
    ["MONTO", "ESTATUS", "LLAMADA AL CLIENTE", "DIAS", "Comentarios"]
)
nuevo_valor = st.text_input("Introduce el nuevo valor para la columna seleccionada:")
if st.button("Aplicar Cambios"):
    try:
        if columna_a_editar in ["MONTO", "DIAS"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_a_editar, columna_a_editar] = nuevo_valor
        st.success("¡Los cambios se han aplicado correctamente!")
    except ValueError:
        st.error("El valor ingresado no es válido para la columna seleccionada.")

# Sección de comentarios por cliente
st.subheader("Comentarios por Cliente")
cliente_comentarios = st.selectbox("Selecciona un cliente para ver o editar comentarios:", cotizaciones["CLIENTE"].unique())
comentario_actual = cotizaciones[cotizaciones["CLIENTE"] == cliente_comentarios]["Comentarios"].values[0]
nuevo_comentario = st.text_area("Comentario Actual:", comentario_actual)
if st.button("Actualizar Comentario"):
    cotizaciones.loc[cotizaciones["CLIENTE"] == cliente_comentarios, "Comentarios"] = nuevo_comentario
    st.success("Comentario actualizado correctamente.")
# Generación de reportes automatizados
st.subheader("Reporte Automático de Cotizaciones Aprobadas")
reporte_aprobadas = cotizaciones[cotizaciones["Semaforo"] == "🟢 Aprobada"]
if not reporte_aprobadas.empty:
    st.write("Cotizaciones aprobadas disponibles para descarga:")
    st.dataframe(reporte_aprobadas[columnas_mostrar], use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Aprobadas",
        data=reporte_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas actualmente.")

# Proyecciones de Ventas Mensuales y Anuales
st.subheader("Proyecciones de Ventas")

def generar_proyecciones(df, columna="MONTO", meses=12):
    df["FECHA ENVIO"] = pd.to_datetime(df["FECHA ENVIO"], errors="coerce")
    df = df.dropna(subset=["FECHA ENVIO"])
    df_proyeccion = df.groupby(df["FECHA ENVIO"].dt.to_period("M"))[columna].sum().reset_index()
    df_proyeccion.rename(columns={"FECHA ENVIO": "Mes", columna: "Monto"}, inplace=True)
    df_proyeccion["Mes"] = df_proyeccion["Mes"].dt.to_timestamp()
    
    ultimo_mes = df_proyeccion["Mes"].max()
    for i in range(1, meses + 1):
        nuevo_mes = ultimo_mes + pd.DateOffset(months=i)
        df_proyeccion = pd.concat([df_proyeccion, pd.DataFrame({"Mes": [nuevo_mes], "Monto": [df_proyeccion["Monto"].mean()]})])
    return df_proyeccion

try:
    proyeccion_mensual = generar_proyecciones(cotizaciones)

    fig_proyeccion_mensual = px.line(
        proyeccion_mensual,
        x="Mes",
        y="Monto",
        title="Proyección Mensual de Ventas",
        labels={"Mes": "Mes", "Monto": "Monto ($)"},
        markers=True
    )
    fig_proyeccion_mensual.update_layout(xaxis_title="Mes", yaxis_title="Monto ($)")
    st.plotly_chart(fig_proyeccion_mensual)

    proyeccion_anual = proyeccion_mensual.groupby(proyeccion_mensual["Mes"].dt.year)["Monto"].sum().reset_index()
    proyeccion_anual.rename(columns={"Mes": "Año", "Monto": "Monto Total"}, inplace=True)

    fig_proyeccion_anual = px.bar(
        proyeccion_anual,
        x="Año",
        y="Monto Total",
        title="Proyección Anual de Ventas",
        labels={"Año": "Año", "Monto Total": "Monto Total ($)"}
    )
    fig_proyeccion_anual.update_layout(xaxis_title="Año", yaxis_title="Monto Total ($)")
    st.plotly_chart(fig_proyeccion_anual)

except Exception as e:
    st.error(f"Error al generar proyecciones: {e}")

# Generar PDF con información general
st.subheader("Generar PDF de Reporte")
if st.button("Generar Reporte en PDF"):
    st.info("Esta funcionalidad está en desarrollo, pero se simula que el PDF se ha generado.")

# Exportar a JSON o CSV para Evidence
st.subheader("Exportar Datos para Evidence")
st.download_button(
    label="Descargar JSON para Evidence",
    data=cotizaciones.to_json(orient="records", indent=4).encode("utf-8"),
    file_name="cotizaciones_evidence.json",
    mime="application/json"
)
st.download_button(
    label="Descargar CSV para Evidence",
    data=cotizaciones.to_csv(index=False).encode("utf-8"),
    file_name="cotizaciones_evidence.csv",
    mime="text/csv"
)

# Función para enviar correo (simulada)
st.subheader("Enviar Reporte por Correo")
correo = st.text_input("Ingresa el correo electrónico:")
if st.button("Enviar Reporte"):
    if correo:
        st.success(f"Reporte enviado a {correo} (simulado).")
    else:
        st.error("Por favor, ingresa un correo válido.")
