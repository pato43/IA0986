import pandas as pd
import streamlit as st
import plotly.express as px

# Ruta del archivo CSV limpio
FILE_PATH = "cleaned_coti.csv"

# Función para cargar y procesar los datos
def cargar_datos(file_path):
    df = pd.read_csv(file_path)
    df_copia = df.copy()

    # Renombrar columnas clave para facilitar su manejo
    df_copia.rename(columns={
        "Monto": "MONTO",
        "Cliente": "CLIENTE",
        "Estatus": "ESTATUS",
        "Fecha_Envio": "FECHA ENVIO",
        "Duracion_Dias": "DIAS",
        "Concepto": "CONCEPTO"
    }, inplace=True)

    # Asignar los valores proporcionados para columnas faltantes o inconsistentes
    vendedores = [
        "Ramiro Rodriguez", "Guillermo Damico", "Juan Alvarado", "Eduardo Manzanares", "Juan Jose Sanchez",
        "Antonio Cabrera", "Juan Carlos Hdz", "Luis Carlos Holt", "Daniel Montero", "Carlos Villanueva",
        "Tere", "Judith Echavarria", "Octavio Farias", "Eduardo Teran", "Sebastian Padilla"
    ]
    clasificaciones = [
        "AA", "A", "A", "AA", "A", "AA", "A", "A", "AA", "AA", "A", "AA", "A", "A", "AA"
    ]
    areas = [
        "Electromecanica", "Construccion", "HVAC eventual", "Electromecanica", "Construccion",
        "Construccion", "HVAC eventual", "Electromecanica", "Construccion", "Electromecanica",
        "Construccion", "Electromecanica", "Construccion", "Construccion", "HVAC eventual"
    ]

    # Asignar valores simulados a las columnas faltantes
    df_copia["VENDEDOR"] = vendedores * (len(df_copia) // len(vendedores)) + vendedores[:len(df_copia) % len(vendedores)]
    df_copia["CLASIFICACION"] = clasificaciones * (len(df_copia) // len(clasificaciones)) + clasificaciones[:len(df_copia) % len(clasificaciones)]
    df_copia["AREA"] = areas * (len(df_copia) // len(areas)) + areas[:len(df_copia) % len(areas)]

    # Crear semáforo para los estados
    df_copia["Semaforo"] = df_copia["ESTATUS"].apply(
        lambda x: "🟢 Aprobada" if x == "APROBADA" else ("🟡 Pendiente" if x == "PENDIENTE" else "🔴 Rechazada")
    )

    # Limpieza y formateo de columnas numéricas
    df_copia["MONTO"] = pd.to_numeric(df_copia["MONTO"].replace({"\$": "", ",": ""}, regex=True), errors="coerce").fillna(0)
    df_copia["DIAS"] = pd.to_numeric(df_copia["DIAS"], errors="coerce").fillna(0)

    return df_copia

# Cargar datos desde el archivo limpio
cotizaciones = cargar_datos(FILE_PATH)

# Configuración inicial del dashboard
st.set_page_config(
    page_title="Dashboard de Cotizaciones",
    page_icon="📊",
    layout="wide"
)

# Introducción
st.title("Dashboard de Cotizaciones")
st.markdown("""
Este dashboard está diseñado para resolver tres problemáticas principales:

1. **Formato unificado para presupuestos y ventas**: Automatiza el análisis unificando ambas perspectivas.
2. **Seguimiento del flujo de cotización**: Rastrea en tiempo real el estado de cada cotización.
3. **Integración con Evidence**: Prepara y exporta datos aprobados automáticamente.
""")

# Copia para simulación y edición
cotizaciones_simuladas = cotizaciones.copy()

# Sección: Estado General de Cotizaciones
st.subheader("Estado General de Cotizaciones")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Esta tabla presenta una vista consolidada de las cotizaciones, incluyendo presupuestos, ventas, y su estado.
""")
columnas_mostrar = [
    "AREA", "CLIENTE", "CONCEPTO", "CLASIFICACION", "VENDEDOR", "FECHA ENVIO", "DIAS", "MONTO", "ESTATUS", "Semaforo"
]

# Filtros dinámicos
filtros = {}
if st.checkbox("Filtrar por Área"):
    filtros['AREA'] = st.multiselect("Selecciona Área(s):", options=cotizaciones_simuladas['AREA'].unique())
if st.checkbox("Filtrar por Clasificación"):
    filtros['CLASIFICACION'] = st.multiselect("Selecciona Clasificación(es):", options=cotizaciones_simuladas['CLASIFICACION'].unique())
if st.checkbox("Filtrar por Vendedor"):
    filtros['VENDEDOR'] = st.multiselect("Selecciona Vendedor(es):", options=cotizaciones_simuladas['VENDEDOR'].unique())

# Aplicar filtros
cotizaciones_filtradas = cotizaciones_simuladas.copy()
for col, values in filtros.items():
    if values:
        cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas[col].isin(values)]

# Mostrar tabla filtrada
st.dataframe(cotizaciones_filtradas[columnas_mostrar], use_container_width=True)

# Métricas generales
st.subheader("Métricas Generales")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Resuma las métricas clave sobre las cotizaciones, presupuestos y ventas.
""")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cotizaciones", len(cotizaciones_filtradas))
col2.metric("Monto Total", f"${cotizaciones_filtradas['MONTO'].sum():,.2f}")
col3.metric("Promedio de Días", f"{cotizaciones_filtradas['DIAS'].mean():.2f}")

# Gráfico de proyección mensual
st.subheader("Proyección de Ventas Mensual")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Proyecta el monto mensual acumulado basado en las cotizaciones actuales.
""")
proyeccion_mensual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:7])["MONTO"].sum().reset_index()
proyeccion_mensual.columns = ["Mes", "Monto"]
fig_proyeccion_mensual = px.line(
    proyeccion_mensual,
    x="Mes",
    y="Monto",
    title="Proyección Mensual de Ventas",
    markers=True
)
st.plotly_chart(fig_proyeccion_mensual)

# Sección: Edición dinámica
st.subheader("Edición Dinámica de Información")
st.markdown("""
**Punto 2: Seguimiento del flujo de cotización**  
Edite información clave de cualquier cotización en tiempo real para mantener los datos actualizados.
""")
cliente_seleccionado = st.selectbox("Selecciona un cliente:", cotizaciones_simuladas["CLIENTE"].unique())
columna_editar = st.selectbox("Selecciona la columna a editar:", ["MONTO", "ESTATUS", "DIAS", "CONCEPTO"])
nuevo_valor = st.text_input("Ingresa el nuevo valor:")
if st.button("Aplicar Cambios"):
    try:
        if columna_editar in ["MONTO", "DIAS"]:
            nuevo_valor = float(nuevo_valor)
        cotizaciones_simuladas.loc[cotizaciones_simuladas["CLIENTE"] == cliente_seleccionado, columna_editar] = nuevo_valor
        st.success("¡Los cambios han sido aplicados exitosamente!")
    except ValueError:
        st.error("El valor ingresado no es válido para la columna seleccionada.")
# Parte 2: Análisis detallado y proyecciones

# Análisis por Vendedor
st.subheader("Análisis por Vendedor")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Esta sección permite analizar el desempeño de cada vendedor en términos de ventas, montos acumulados, y cotizaciones realizadas.
""")
vendedor_agrupado = cotizaciones_filtradas.groupby("VENDEDOR").agg(
    Total_Cotizaciones=("CLIENTE", "count"),
    Total_Monto=("MONTO", "sum"),
    Promedio_Dias=("DIAS", "mean")
).reset_index()
st.dataframe(vendedor_agrupado, use_container_width=True)

# Gráfico de Barras: Ventas por Vendedor
fig_vendedor = px.bar(
    vendedor_agrupado,
    x="VENDEDOR",
    y="Total_Monto",
    title="Monto Total por Vendedor",
    labels={"Total_Monto": "Monto Total ($)", "VENDEDOR": "Vendedor"},
    text="Total_Monto"
)
st.plotly_chart(fig_vendedor)

# Análisis por Área
st.subheader("Análisis por Área")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Esta sección muestra el desempeño por área, ayudando a identificar las áreas más productivas.
""")
area_agrupada = cotizaciones_filtradas.groupby("AREA").agg(
    Total_Cotizaciones=("CLIENTE", "count"),
    Total_Monto=("MONTO", "sum")
).reset_index()
st.dataframe(area_agrupada, use_container_width=True)

# Gráfico de Barras: Ventas por Área
fig_area = px.bar(
    area_agrupada,
    x="AREA",
    y="Total_Monto",
    title="Monto Total por Área",
    labels={"Total_Monto": "Monto Total ($)", "AREA": "Área"},
    text="Total_Monto"
)
st.plotly_chart(fig_area)

# Exportación de Datos Aprobados
st.subheader("Exportación de Datos Aprobados")
st.markdown("""
**Punto 3: Integración con Evidence**  
En esta sección, puedes exportar los datos de cotizaciones aprobadas para integrarlos fácilmente en otros sistemas.
""")
cotizaciones_aprobadas = cotizaciones_filtradas[cotizaciones_filtradas["Semaforo"] == "🟢 Aprobada"]

if not cotizaciones_aprobadas.empty:
    st.dataframe(cotizaciones_aprobadas[columnas_mostrar], use_container_width=True)
    st.download_button(
        label="Descargar JSON de Cotizaciones Aprobadas",
        data=cotizaciones_aprobadas.to_json(orient="records", indent=4).encode("utf-8"),
        file_name="cotizaciones_aprobadas.json",
        mime="application/json"
    )
    st.download_button(
        label="Descargar CSV de Cotizaciones Aprobadas",
        data=cotizaciones_aprobadas.to_csv(index=False).encode("utf-8"),
        file_name="cotizaciones_aprobadas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones aprobadas para exportar.")

# Generación de Reportes Personalizados
st.subheader("Generación de Reportes Personalizados")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Genera reportes detallados con información clave para toma de decisiones.
""")
reporte_agrupado = cotizaciones_filtradas.groupby(["VENDEDOR", "AREA"]).agg(
    Total_Cotizaciones=("CLIENTE", "count"),
    Total_Monto=("MONTO", "sum"),
    Promedio_Dias=("DIAS", "mean")
).reset_index()

st.dataframe(reporte_agrupado, use_container_width=True)

# Botón para descargar el reporte en CSV
st.download_button(
    label="Descargar Reporte Personalizado (CSV)",
    data=reporte_agrupado.to_csv(index=False).encode("utf-8"),
    file_name="reporte_personalizado.csv",
    mime="text/csv"
)
# Parte 3: Seguimiento y Reportes Automatizados

# Seguimiento detallado del flujo de cotización
st.subheader("Seguimiento del Flujo de Cotización")
st.markdown("""
**Punto 2: Seguimiento del flujo de cotización**  
Esta tabla permite rastrear cada cotización, mostrando:
- Cliente asociado.
- Responsable del levantamiento.
- Tiempo transcurrido desde que se envió hasta su estado actual.
""")
seguimiento_columnas = ["CLIENTE", "VENDEDOR", "CONCEPTO", "FECHA ENVIO", "DIAS", "ESTATUS", "Semaforo"]
st.dataframe(cotizaciones_filtradas[seguimiento_columnas], use_container_width=True)

# Generación de reportes detallados por flujo de cotización
st.subheader("Reporte de Cotizaciones Pendientes")
st.markdown("""
**Punto 2: Seguimiento del flujo de cotización**  
Genera un reporte de todas las cotizaciones pendientes para priorizar envíos o revisiones atrasadas.
""")
cotizaciones_pendientes = cotizaciones_filtradas[cotizaciones_filtradas["Semaforo"] == "🟡 Pendiente"]

if not cotizaciones_pendientes.empty:
    st.dataframe(cotizaciones_pendientes[columnas_mostrar], use_container_width=True)
    st.download_button(
        label="Descargar Reporte de Cotizaciones Pendientes",
        data=cotizaciones_pendientes.to_csv(index=False).encode("utf-8"),
        file_name="reporte_cotizaciones_pendientes.csv",
        mime="text/csv"
    )
else:
    st.info("No hay cotizaciones pendientes.")

# Seguimiento de aprobaciones y tiempos
st.subheader("Seguimiento de Cotizaciones Aprobadas")
st.markdown("""
**Punto 3: Integración con Evidence**  
Muestra las cotizaciones aprobadas listas para ser capturadas en Evidence.  
Incluye los tiempos transcurridos desde que se levantó hasta su aprobación.
""")
cotizaciones_aprobadas["Dias_Aprobacion"] = cotizaciones_aprobadas["DIAS"]
st.dataframe(cotizaciones_aprobadas[seguimiento_columnas + ["Dias_Aprobacion"]], use_container_width=True)

# Gráfico de Proyección Mensual
st.subheader("Proyección de Ventas para el Próximo Mes")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Proyecta las ventas esperadas para el próximo mes basado en el historial actual.
""")
proyeccion_mensual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:7])["MONTO"].sum().reset_index()
proyeccion_mensual.columns = ["Mes", "Monto"]
fig_proyeccion_mensual = px.line(
    proyeccion_mensual,
    x="Mes",
    y="Monto",
    title="Proyección Mensual de Ventas",
    markers=True
)
st.plotly_chart(fig_proyeccion_mensual)

# Gráfico de Proyección Anual
st.subheader("Proyección Anual de Ventas")
st.markdown("""
**Punto 1: Formato unificado para presupuestos y ventas**  
Proyecta el monto anual acumulado basado en las cotizaciones actuales.
""")
proyeccion_anual = cotizaciones_filtradas.groupby(cotizaciones_filtradas["FECHA ENVIO"].str[:4])["MONTO"].sum().reset_index()
proyeccion_anual.columns = ["Año", "Monto"]
fig_proyeccion_anual = px.line(
    proyeccion_anual,
    x="Año",
    y="Monto",
    title="Proyección Anual de Ventas",
    markers=True
)
st.plotly_chart(fig_proyeccion_anual)

# Envío de Reportes por Correo
st.subheader("Envío de Reportes por Correo")
st.markdown("""
**Facilita la distribución de reportes generados automáticamente.**  
Envía reportes pendientes o aprobados por correo.
""")
correo = st.text_input("Ingresa el correo electrónico:")
if st.button("Enviar Reporte"):
    if correo:
        st.success(f"Reporte enviado exitosamente a {correo} (simulado).")
    else:
        st.error("Por favor, ingresa un correo válido.")
