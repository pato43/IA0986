import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración inicial
st.set_page_config(
    page_title="Sistema de Evaluación y Gestión de Cotizaciones",
    page_icon="💼",
    layout="wide",
)

# Encabezado principal
st.title("Sistema de Evaluación y Gestión de Cotizaciones 💼")
st.write(
    """
    Este sistema permite gestionar cotizaciones, evaluar su complejidad y relevancia, 
    y administrar usuarios y roles de manera interactiva.
    """
)

# --------------------- Clasificación de Cotizaciones ---------------------
st.header("Clasificación de Cotizaciones 📄")

# Tipos de cotización definidos
tipos_cotizacion = {
    "Doble A": {"min": 200000, "max": 500000},
    "Triple A": {"min": 1000000, "max": 20000000},
}

# Datos simulados de cotizaciones
cotizaciones_df = pd.DataFrame({
    "ID_Cotización": range(1, 11),
    "Cliente": [f"Cliente {i}" for i in range(1, 11)],
    "Monto": np.random.randint(100000, 5000000, 10),
    "Complejidad": np.random.choice(["Alta", "Media", "Baja"], 10),
    "Estatus": np.random.choice(["Aceptada", "Pendiente", "Rechazada"], 10),
})

# Función para clasificar cotizaciones
def clasificar_cotizacion(row):
    for tipo, rango in tipos_cotizacion.items():
        if rango["min"] <= row["Monto"] <= rango["max"]:
            return tipo
    return "Otra"

cotizaciones_df["Clasificación"] = cotizaciones_df.apply(clasificar_cotizacion, axis=1)

# Mostrar tabla interactiva
st.write("### Cotizaciones Clasificadas:")
st.dataframe(cotizaciones_df)

# Generar un DataFrame con las clasificaciones y sus conteos
clasificacion_resumen = cotizaciones_df["Clasificación"].value_counts().reset_index()
clasificacion_resumen.columns = ["Clasificación", "Cantidad"]

# Gráfico interactivo de clasificación
st.write("### Distribución por Clasificación:")
fig_clasificacion = px.bar(
    clasificacion_resumen,
    x="Clasificación",
    y="Cantidad",
    labels={"Clasificación": "Tipo de Cotización", "Cantidad": "Número de Cotizaciones"},
    title="Distribución de Cotizaciones por Clasificación",
    text_auto=True,
    color="Clasificación",
)
st.plotly_chart(fig_clasificacion, use_container_width=True)

# --------------------- Captura de Cotizaciones ---------------------
st.header("Captura de Cotizaciones ✏️")

# Formulario para captura de cotización
st.write("### Captura Manual:")
id_cotizacion = st.number_input("ID Cotización", min_value=1, step=1, value=len(cotizaciones_df) + 1)
cliente = st.text_input("Cliente", value=f"Cliente {len(cotizaciones_df) + 1}")
monto = st.number_input("Monto (MXN)", min_value=0, step=1000)
complejidad = st.selectbox("Complejidad", ["Alta", "Media", "Baja"])
estatus = st.selectbox("Estatus", ["Aceptada", "Pendiente", "Rechazada"])

# Botón para capturar datos
if st.button("Capturar Cotización"):
    nueva_cotizacion = {
        "ID_Cotización": id_cotizacion,
        "Cliente": cliente,
        "Monto": monto,
        "Complejidad": complejidad,
        "Estatus": estatus,
        "Clasificación": clasificar_cotizacion({"Monto": monto}),
    }
    cotizaciones_df = pd.concat([cotizaciones_df, pd.DataFrame([nueva_cotizacion])], ignore_index=True)
    st.success("Cotización capturada correctamente.")
    st.dataframe(cotizaciones_df)

# Opción para capturar datos simulados de campo
st.write("### Captura Simulada desde Campo:")
captura_simulada = st.radio(
    "Seleccione un tipo de captura:",
    ["Vía telefónica", "En campo", "Automatizada"]
)
st.info(f"Captura seleccionada: {captura_simulada}")

# Visualización de cambios actualizados
st.write("### Cotizaciones Actualizadas:")
st.dataframe(cotizaciones_df)
# --------------------- Asignación y Flujo de Trabajo ---------------------
st.header("Asignación y Flujo de Trabajo 📋")

# Simulación de usuarios y roles
usuarios_roles = pd.DataFrame({
    "Usuario": ["Antonia", "Eduardo", "Luis Carlos", "Gerente A", "Vendedor 1", "Vendedor 2"],
    "Rol": ["Supervisora", "Gerente Estratégico", "Gerente Estratégico", "Coordinador", "Vendedor", "Vendedor"],
})

# Mostrar tabla de roles
st.write("### Roles y Responsabilidades:")
st.dataframe(usuarios_roles)

# Flujo de trabajo de las cotizaciones
st.write("### Flujo de Trabajo de las Cotizaciones:")
flujo_trabajo = [
    {"Etapa": "Captura inicial", "Responsable": "Vendedor"},
    {"Etapa": "Clasificación", "Responsable": "Antonia (Supervisora)"},
    {"Etapa": "Revisión", "Responsable": "Coordinador o Gerente"},
    {"Etapa": "Aprobación Estratégica", "Responsable": "Eduardo o Luis Carlos"},
    {"Etapa": "Presupuesto Final", "Responsable": "Gerente Estratégico"},
]
df_flujo = pd.DataFrame(flujo_trabajo)
st.dataframe(df_flujo)

# Asignación de cotizaciones a usuarios
st.write("### Asignación de Cotizaciones:")
usuario_seleccionado = st.selectbox("Selecciona un usuario para asignar cotizaciones:", usuarios_roles["Usuario"])
cotizaciones_disponibles = cotizaciones_df[cotizaciones_df["Estatus"] == "Pendiente"]

# Tabla de cotizaciones pendientes
st.write("Cotizaciones pendientes:")
st.dataframe(cotizaciones_disponibles)

# Botón para asignar cotización
cotizacion_asignada = st.selectbox("Selecciona una cotización para asignar:", cotizaciones_disponibles["ID_Cotización"])
if st.button("Asignar Cotización"):
    st.success(f"Cotización {cotizacion_asignada} asignada a {usuario_seleccionado}.")

# --------------------- Monitoreo y Alertas ---------------------
st.header("Monitoreo y Alertas 🚦")

# Simulación de estados de las cotizaciones
cotizaciones_df["Días Restantes"] = np.random.randint(-5, 10, len(cotizaciones_df))
cotizaciones_df["Estado Semáforo"] = pd.cut(
    cotizaciones_df["Días Restantes"],
    bins=[-float("inf"), 0, 3, float("inf")],
    labels=["Rojo", "Amarillo", "Verde"]
)

# Sistema de semáforos
st.write("### Sistema de Semáforos:")
st.markdown(
    """
    - **Rojo:** Tareas vencidas.
    - **Amarillo:** Tareas próximas a vencer.
    - **Verde:** Tareas completadas o con tiempo suficiente.
    """
)

# Mostrar cotizaciones con semáforo
st.write("### Estado de las Cotizaciones:")
fig_semaforo = px.bar(
    cotizaciones_df,
    x="ID_Cotización",
    y="Días Restantes",
    color="Estado Semáforo",
    title="Estado de las Cotizaciones (Sistema de Semáforos)",
    color_discrete_map={"Rojo": "red", "Amarillo": "yellow", "Verde": "green"},
    text_auto=True,
)
st.plotly_chart(fig_semaforo, use_container_width=True)

# Filtrar por estado de semáforo
estado_filtrado = st.selectbox("Filtrar por estado de semáforo:", ["Todos", "Rojo", "Amarillo", "Verde"])
if estado_filtrado != "Todos":
    cotizaciones_filtradas = cotizaciones_df[cotizaciones_df["Estado Semáforo"] == estado_filtrado]
else:
    cotizaciones_filtradas = cotizaciones_df

st.write("### Cotizaciones Filtradas por Estado:")
st.dataframe(cotizaciones_filtradas)

# Alertas personalizadas
st.write("### Alertas Personalizadas:")
for _, row in cotizaciones_filtradas.iterrows():
    if row["Estado Semáforo"] == "Rojo":
        st.error(f"⚠️ Cotización {row['ID_Cotización']} está vencida. Urgente revisión.")
    elif row["Estado Semáforo"] == "Amarillo":
        st.warning(f"⚠️ Cotización {row['ID_Cotización']} está próxima a vencer.")
    else:
        st.success(f"✔️ Cotización {row['ID_Cotización']} está en buen estado.")
# --------------------- Evaluaciones y Métricas ---------------------
st.header("Evaluaciones y Métricas 📊")

# Timeline del proyecto
st.subheader("Timeline del Proyecto 📅")
cotizaciones_df["Días para Finalizar"] = cotizaciones_df["Días Restantes"] + np.random.randint(5, 30, len(cotizaciones_df))
fig_timeline = px.timeline(
    cotizaciones_df,
    x_start="Días Restantes",
    x_end="Días para Finalizar",
    y="Cliente",
    title="Timeline de Proyectos por Cliente",
    color="Estado Semáforo",
    labels={"Días Restantes": "Inicio", "Días para Finalizar": "Fin"},
    color_discrete_map={"Rojo": "red", "Amarillo": "yellow", "Verde": "green"},
)
fig_timeline.update_yaxes(categoryorder="total ascending")
st.plotly_chart(fig_timeline, use_container_width=True)

# Indicadores visuales para evaluar completitud de datos
st.subheader("Checkpoints de Evaluación ✅")
cotizaciones_df["Check Completo"] = cotizaciones_df.apply(
    lambda x: "✅ Completo" if x["Monto"] > 100000 and x["Estado Semáforo"] == "Verde" else "⚠️ Pendiente", axis=1
)
st.write("### Estado de Checkpoints:")
st.dataframe(cotizaciones_df[["ID_Cotización", "Cliente", "Check Completo"]])

# Generación automática de bonos
st.subheader("Bonos Automáticos 💰")
cotizaciones_df["Bono"] = cotizaciones_df.apply(
    lambda x: 5000 if x["Estado Semáforo"] == "Verde" and x["Estatus"] == "Aceptada" else 0, axis=1
)
st.write("### Bonos Generados:")
st.dataframe(cotizaciones_df[["ID_Cotización", "Cliente", "Bono"]])

# --------------------- Seguimiento Postventa ---------------------
st.header("Seguimiento Postventa 📦")

# Indicadores de avance
st.subheader("Indicadores de Avance 📈")
cotizaciones_df["Porcentaje Avance"] = np.random.randint(50, 100, len(cotizaciones_df))
fig_avance = px.bar(
    cotizaciones_df,
    x="Cliente",
    y="Porcentaje Avance",
    title="Porcentaje de Avance por Proyecto",
    text_auto=True,
    color="Porcentaje Avance",
    color_continuous_scale=px.colors.sequential.Viridis,
)
st.plotly_chart(fig_avance, use_container_width=True)

# Retroalimentación y mejoras
st.subheader("Retroalimentación y Mejoras 📢")
st.write("### Comentarios de Clientes:")
retroalimentacion = st.text_area("Ingresa comentarios sobre mejoras y experiencias:", height=150)
if st.button("Guardar Retroalimentación"):
    st.success("Retroalimentación guardada exitosamente.")
    st.info(f"Comentarios ingresados: {retroalimentacion}")

# --------------------- Generación de Reportes ---------------------
st.header("Generación de Reportes 📑")

# Personalización del reporte
st.subheader("Personaliza tu Reporte 📋")
columnas_seleccionadas = st.multiselect(
    "Selecciona las columnas para incluir en el reporte:",
    cotizaciones_df.columns,
    default=["ID_Cotización", "Cliente", "Monto", "Estatus"]
)

# Generar CSV
@st.cache_data
def generar_csv_reporte(df, columnas):
    return df[columnas].to_csv(index=False).encode('utf-8')

csv_reporte = generar_csv_reporte(cotizaciones_df, columnas_seleccionadas)
st.download_button(
    label="Descargar Reporte en CSV 📥",
    data=csv_reporte,
    file_name="reporte_cotizaciones.csv",
    mime="text/csv",
)

# Generar PDF
st.write("### Generación de Reporte en PDF:")
if st.button("Generar Reporte PDF"):
    st.info("⚠️ La funcionalidad de PDF está en desarrollo. Por ahora, descarga el CSV.")

# Resumen general
st.subheader("Resumen General 🌟")
st.write("### Estadísticas de Cotizaciones:")
st.write(cotizaciones_df[["Monto", "Porcentaje Avance", "Bono"]].describe())
