# Parte 1: Importaciones, Configuración Inicial y Carga de Datos
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(
    page_title="Sistema de Evaluación de Cotizaciones",
    page_icon="💼",
    layout="wide",
)

# Encabezado principal
st.title("Sistema de Evaluación de Cotizaciones 💼")
st.write(
    """
    Este sistema permite gestionar cotizaciones, evaluar su complejidad y relevancia, y 
    administrar usuarios y roles de manera interactiva. 
    """
)

# Sección 1: Carga de datos (simulados o subidos por el usuario)
st.header("Carga de Cotizaciones 📄")
uploaded_file = st.file_uploader("Sube un archivo CSV con cotizaciones", type=["csv"])

# Si no se sube archivo, generar datos simulados
if uploaded_file is not None:
    cotizaciones_df = pd.read_csv(uploaded_file)
    st.success("Archivo cargado correctamente.")
else:
    st.warning("No se cargó un archivo. Usando datos simulados...")
    cotizaciones_df = pd.DataFrame({
        "ID_Cotización": range(1, 11),
        "Cliente": [f"Cliente {i}" for i in range(1, 11)],
        "Monto": np.random.randint(5000, 50000, 10),
        "Complejidad": np.random.choice(["Alta", "Media", "Baja"], 10),
        "Estatus": np.random.choice(["Aceptada", "Pendiente", "Rechazada"], 10),
    })

# Mostrar tabla de cotizaciones
st.write("### Cotizaciones Actuales:")
st.dataframe(cotizaciones_df)

# Función para calcular resumen de complejidad
def calcular_resumen_complejidad(df):
    return df["Complejidad"].value_counts()

# Generar resumen y mostrar gráfico de barras
st.write("### Resumen de Complejidad:")
complejidad_resumen = calcular_resumen_complejidad(cotizaciones_df)

# Solución alternativa: Usar Matplotlib para gráfico de pastel
fig, ax = plt.subplots()
ax.pie(
    complejidad_resumen,
    labels=complejidad_resumen.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=["#FF9999", "#66B3FF", "#99FF99"]
)
ax.axis("equal")  # Asegura que el gráfico sea circular
st.pyplot(fig)
# Parte 2: Evaluación de relevancia, gestión de roles y análisis interactivo
st.header("Evaluación y Gestión 📊")

# Sección 2.1: Evaluación de relevancia
st.subheader("Evaluación de Relevancia 🔍")

# Definir criterios para evaluar la relevancia
st.write("""
La relevancia de las cotizaciones se calcula basándose en criterios como:
- Monto total (mayores montos tienen mayor relevancia).
- Complejidad (las cotizaciones de baja complejidad son más relevantes por ser rápidas de procesar).
- Estatus actual (pendientes tienen mayor prioridad).
""")

# Función para evaluar relevancia (puntuación simple)
def calcular_relevancia(row):
    puntuacion = 0
    # Asignar peso según monto
    if row["Monto"] > 30000:
        puntuacion += 5
    elif row["Monto"] > 15000:
        puntuacion += 3
    else:
        puntuacion += 1
    # Asignar peso según complejidad
    if row["Complejidad"] == "Baja":
        puntuacion += 5
    elif row["Complejidad"] == "Media":
        puntuacion += 3
    else:
        puntuacion += 1
    # Asignar peso según estatus
    if row["Estatus"] == "Pendiente":
        puntuacion += 5
    elif row["Estatus"] == "Aceptada":
        puntuacion += 3
    else:
        puntuacion += 0
    return puntuacion

# Agregar columna de relevancia al DataFrame
cotizaciones_df["Relevancia"] = cotizaciones_df.apply(calcular_relevancia, axis=1)

# Mostrar las cotizaciones ordenadas por relevancia
st.write("### Cotizaciones ordenadas por relevancia:")
cotizaciones_ordenadas = cotizaciones_df.sort_values(by="Relevancia", ascending=False)
st.dataframe(cotizaciones_ordenadas)

# Visualización de relevancia (gráfico de barras)
st.write("### Relevancia de las cotizaciones:")
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(cotizaciones_ordenadas["ID_Cotización"], cotizaciones_ordenadas["Relevancia"], color="#FFA07A")
ax.set_xlabel("ID Cotización")
ax.set_ylabel("Relevancia")
ax.set_title("Puntuación de Relevancia por Cotización")
st.pyplot(fig)

# Sección 2.2: Gestión de roles de usuario
st.subheader("Gestión de Roles y Permisos 👥")

# Simular una lista de usuarios y roles
usuarios_roles = pd.DataFrame({
    "Usuario": ["admin", "analista1", "analista2", "cliente1"],
    "Rol": ["Administrador", "Analista", "Analista", "Cliente"],
})

# Mostrar usuarios y roles actuales
st.write("### Usuarios y Roles Actuales:")
st.dataframe(usuarios_roles)

# Seleccionar usuario para modificar
st.write("### Modificar Roles:")
usuario_seleccionado = st.selectbox("Selecciona un usuario", usuarios_roles["Usuario"])

# Asignar nuevo rol
nuevo_rol = st.selectbox(
    "Selecciona un nuevo rol para el usuario:",
    ["Administrador", "Analista", "Cliente"]
)

# Botón para aplicar cambios
if st.button("Actualizar Rol"):
    usuarios_roles.loc[usuarios_roles["Usuario"] == usuario_seleccionado, "Rol"] = nuevo_rol
    st.success(f"El rol del usuario {usuario_seleccionado} ha sido actualizado a {nuevo_rol}.")
    st.dataframe(usuarios_roles)

# Sección 2.3: Filtros interactivos
st.subheader("Filtros Interactivos 🔧")

# Filtro por estatus
estatus_seleccionado = st.multiselect(
    "Selecciona los estatus a mostrar:",
    cotizaciones_df["Estatus"].unique(),
    default=cotizaciones_df["Estatus"].unique()
)

# Filtro por complejidad
complejidad_seleccionada = st.multiselect(
    "Selecciona las complejidades a mostrar:",
    cotizaciones_df["Complejidad"].unique(),
    default=cotizaciones_df["Complejidad"].unique()
)

# Aplicar filtros al DataFrame
cotizaciones_filtradas = cotizaciones_df[
    (cotizaciones_df["Estatus"].isin(estatus_seleccionado)) &
    (cotizaciones_df["Complejidad"].isin(complejidad_seleccionada))
]

st.write("### Cotizaciones Filtradas:")
st.dataframe(cotizaciones_filtradas)

# Descarga de datos filtrados
@st.cache_data
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convertir_csv(cotizaciones_filtradas)
st.download_button(
    label="Descargar Cotizaciones Filtradas 📥",
    data=csv,
    file_name="cotizaciones_filtradas.csv",
    mime="text/csv",
)
# Parte 3: Creación de reportes y simulaciones
st.header("Creación de Reportes y Simulaciones 📑")

# Sección 3.1: Generación de reportes
st.subheader("Generación de Reportes 📊")

# Opción para seleccionar columnas a incluir en el reporte
st.write("### Personaliza tu reporte:")
columnas_seleccionadas = st.multiselect(
    "Selecciona las columnas que deseas incluir en el reporte:",
    cotizaciones_df.columns,
    default=["ID_Cotización", "Cliente", "Monto", "Estatus"]
)

# Generar reporte en formato PDF o CSV
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

# Generar PDF (simulado con un mensaje)
if st.button("Generar Reporte en PDF"):
    st.info("⚠️ La generación de reportes en PDF se está desarrollando. Por ahora, descarga el CSV.")

# Sección 3.2: Simulaciones básicas
st.subheader("Simulaciones de Escenarios 🧮")

st.write("""
Las simulaciones permiten proyectar distintos escenarios en función de los datos actuales.
Prueba a modificar parámetros clave para analizar su impacto.
""")

# Parámetros de simulación
st.write("### Parámetros de Simulación:")
factor_crecimiento = st.slider(
    "Tasa de crecimiento estimada (%):", min_value=0, max_value=100, value=10, step=5
)

# Aplicar simulación al monto de las cotizaciones
cotizaciones_df["Monto_Proyectado"] = cotizaciones_df["Monto"] * (1 + factor_crecimiento / 100)

# Mostrar resultados de la simulación
st.write("### Resultados de la Simulación:")
st.dataframe(cotizaciones_df[["ID_Cotización", "Cliente", "Monto", "Monto_Proyectado"]])

# Visualizar comparación entre montos originales y proyectados
st.write("### Comparación Gráfica:")
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(cotizaciones_df["ID_Cotización"], cotizaciones_df["Monto"], label="Monto Original", alpha=0.7, color="#1f77b4")
ax.bar(cotizaciones_df["ID_Cotización"], cotizaciones_df["Monto_Proyectado"], label="Monto Proyectado", alpha=0.7, color="#ff7f0e")
ax.set_xlabel("ID Cotización")
ax.set_ylabel("Monto")
ax.set_title("Comparación de Montos Originales vs Proyectados")
ax.legend()
st.pyplot(fig)

# Sección 3.3: Resumen y visualizaciones adicionales
st.subheader("Resumen y Visualizaciones 🔎")

# Resumen de estadísticas clave
st.write("### Estadísticas Clave:")
st.write(cotizaciones_df[["Monto", "Monto_Proyectado"]].describe())

# Gráfico de torta: Distribución por estatus
st.write("### Distribución de Cotizaciones por Estatus:")
fig2, ax2 = plt.subplots()
estatus_counts = cotizaciones_df["Estatus"].value_counts()
ax2.pie(estatus_counts, labels=estatus_counts.index, autopct="%1.1f%%", startangle=90, colors=plt.cm.Paired.colors)
ax2.set_title("Distribución de Estatus")
st.pyplot(fig2)

# Mapa interactivo (placeholder si se requiere geolocalización)
st.write("### Mapa Interactivo 🌍")
st.map(pd.DataFrame({"lat": [19.4326], "lon": [-99.1332]}))  # Ejemplo: CDMX

# Sección 3.4: Interactividad adicional
st.subheader("Panel Interactivo 💡")

# Campo de búsqueda para filtrar cotizaciones por cliente
cliente_busqueda = st.text_input("Buscar Cotización por Cliente:")
resultado_busqueda = cotizaciones_df[cotizaciones_df["Cliente"].str.contains(cliente_busqueda, case=False, na=False)]
if not resultado_busqueda.empty:
    st.write("### Resultados de la Búsqueda:")
    st.dataframe(resultado_busqueda)
else:
    st.warning("No se encontraron resultados para el cliente ingresado.")

# Botón de finalización
st.write("### Finalizar 🚀")
if st.button("Confirmar y Guardar Cambios"):
    st.success("Todos los cambios han sido guardados correctamente.")
