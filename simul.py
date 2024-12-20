import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuración inicial
st.set_page_config(page_title="Gestión de Cotizaciones", layout="wide")

# Simulación de datos de cotizaciones
cotizaciones_data = {
    "ID_Cotización": [1, 2, 3],
    "Cliente": ["Cliente A", "Cliente B", "Cliente C"],
    "Monto": [200000, 500000, 1000000],
    "Complejidad": ["Media", "Alta", "Baja"],
    "Estatus": ["Pendiente", "En Proceso", "Finalizada"],
    "Fecha_Registro": [datetime.now() - timedelta(days=5), 
                       datetime.now() - timedelta(days=10), 
                       datetime.now() - timedelta(days=15)],
    "Días_Restantes": [7, 14, 20]
}

# Simulación de usuarios
usuarios_data = {
    "ID_Usuario": [101, 102, 103],
    "Nombre": ["Antonia", "Luis Carlos", "Eduardo"],
    "Rol": ["Coordinador", "Vendedor", "Gerente"],
    "Acceso": ["Total", "Limitado", "Total"]
}

# Convertir a DataFrame
cotizaciones_df = pd.DataFrame(cotizaciones_data)
usuarios_df = pd.DataFrame(usuarios_data)

# Título principal
st.title("Sistema de Gestión de Cotizaciones y Monitoreo")

# Mostrar las bases de datos simuladas en la barra lateral
st.sidebar.markdown("### Bases de Datos Simuladas")
if st.sidebar.checkbox("Mostrar cotizaciones"):
    st.sidebar.write(cotizaciones_df)

if st.sidebar.checkbox("Mostrar usuarios"):
    st.sidebar.write(usuarios_df)
# Segunda parte del sistema: Agregar funcionalidad interactiva

# Sección 1: Visualización y filtros avanzados
st.header("Visualización de Cotizaciones")

# Filtro por cliente
cliente_seleccionado = st.selectbox("Selecciona un cliente para filtrar cotizaciones:", ["Todos"] + cotizaciones_df["Cliente"].tolist())
if cliente_seleccionado != "Todos":
    cotizaciones_filtradas = cotizaciones_df[cotizaciones_df["Cliente"] == cliente_seleccionado]
else:
    cotizaciones_filtradas = cotizaciones_df

# Filtro por estatus
estatus_seleccionado = st.multiselect(
    "Filtrar cotizaciones por estatus:",
    options=cotizaciones_df["Estatus"].unique(),
    default=cotizaciones_df["Estatus"].unique()
)
cotizaciones_filtradas = cotizaciones_filtradas[cotizaciones_filtradas["Estatus"].isin(estatus_seleccionado)]

# Mostrar resultados filtrados
st.write(f"### Cotizaciones para: {cliente_seleccionado if cliente_seleccionado != 'Todos' else 'Todos los clientes'}")
st.dataframe(cotizaciones_filtradas)

# Sección 2: Agregar una nueva cotización
st.header("Agregar Nueva Cotización")
with st.form("form_agregar_cotizacion"):
    nuevo_cliente = st.text_input("Nombre del cliente")
    nuevo_monto = st.number_input("Monto estimado (en MXN)", min_value=1000, step=1000)
    nueva_complejidad = st.selectbox("Nivel de complejidad", ["Baja", "Media", "Alta"])
    nuevo_estatus = st.selectbox("Estatus inicial", ["Pendiente", "En Proceso", "Finalizada"])
    nueva_fecha_registro = st.date_input("Fecha de registro", value=datetime.now())
    dias_restantes = st.number_input("Días restantes para concluir", min_value=1, step=1)

    # Botón para agregar
    submit_button = st.form_submit_button("Agregar Cotización")
    if submit_button:
        nuevo_id = cotizaciones_df["ID_Cotización"].max() + 1
        nueva_cotizacion = {
            "ID_Cotización": nuevo_id,
            "Cliente": nuevo_cliente,
            "Monto": nuevo_monto,
            "Complejidad": nueva_complejidad,
            "Estatus": nuevo_estatus,
            "Fecha_Registro": nueva_fecha_registro,
            "Días_Restantes": dias_restantes,
        }
        cotizaciones_df = pd.concat([cotizaciones_df, pd.DataFrame([nueva_cotizacion])], ignore_index=True)
        st.success(f"¡Nueva cotización agregada para {nuevo_cliente}!")

# Sección 3: Resumen y estadísticas
st.header("Resumen y Estadísticas Generales")
st.write("Aquí se muestran métricas clave relacionadas con las cotizaciones:")

# Resumen de estatus
estatus_resumen = cotizaciones_df["Estatus"].value_counts()
st.bar_chart(estatus_resumen)

# Resumen de complejidades
complejidad_resumen = cotizaciones_df["Complejidad"].value_counts()
st.write("### Distribución por Complejidad")
st.pie_chart(data=complejidad_resumen, labels=complejidad_resumen.index)

# Promedio de montos
promedio_monto = cotizaciones_df["Monto"].mean()
st.metric("Monto Promedio de Cotizaciones (MXN)", f"${promedio_monto:,.2f}")

# Promedio de días restantes
promedio_dias = cotizaciones_df["Días_Restantes"].mean()
st.metric("Días Restantes Promedio", f"{promedio_dias:.1f} días")
# Tercera parte del sistema: Funcionalidades avanzadas y manejo de roles

# Sección 4: Administración de Usuarios y Roles
st.header("Administración de Usuarios y Roles")

# Tabla de roles (demostrativa)
roles_data = [
    {"Usuario": "admin", "Rol": "Administrador", "Permisos": "Todos"},
    {"Usuario": "analista01", "Rol": "Analista", "Permisos": "Lectura, Estadísticas"},
    {"Usuario": "ventas02", "Rol": "Ventas", "Permisos": "Lectura, Agregar Cotizaciones"}
]
roles_df = pd.DataFrame(roles_data)

# Mostrar tabla
st.write("### Usuarios y sus roles:")
st.dataframe(roles_df)

# Agregar nuevo usuario
with st.form("form_agregar_usuario"):
    nuevo_usuario = st.text_input("Nombre de usuario")
    nuevo_rol = st.selectbox("Seleccionar rol", ["Administrador", "Analista", "Ventas"])
    boton_agregar_usuario = st.form_submit_button("Agregar Usuario")
    if boton_agregar_usuario:
        nuevo_registro = {"Usuario": nuevo_usuario, "Rol": nuevo_rol, "Permisos": "Por Definir"}
        roles_df = pd.concat([roles_df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        st.success(f"¡Usuario {nuevo_usuario} agregado con rol {nuevo_rol}!")

# Sección 5: Evaluación de Complejidad y Relevancia
st.header("Evaluación de Complejidad y Relevancia")

# Selección de cotización para evaluar
st.write("Selecciona una cotización para evaluar:")
cotizacion_id = st.selectbox("ID de Cotización", cotizaciones_df["ID_Cotización"])

# Mostrar detalles de la cotización seleccionada
cotizacion_seleccionada = cotizaciones_df[cotizaciones_df["ID_Cotización"] == cotizacion_id].iloc[0]
st.write(f"**Cliente:** {cotizacion_seleccionada['Cliente']}")
st.write(f"**Monto:** ${cotizacion_seleccionada['Monto']:,.2f}")
st.write(f"**Complejidad:** {cotizacion_seleccionada['Complejidad']}")
st.write(f"**Estatus:** {cotizacion_seleccionada['Estatus']}")

# Evaluación simulada (demostrativa)
relevancia_score = round(cotizacion_seleccionada["Monto"] / 1000, 2)
st.write(f"### Evaluación de Relevancia: {relevancia_score} puntos")
st.progress(min(relevancia_score / 10, 1.0))

# Sección 6: Funcionalidades demostrativas
st.header("Sección Demostrativa")

# Botón para "Exportar Cotizaciones" (demostración)
if st.button("Exportar Cotizaciones a CSV"):
    cotizaciones_df.to_csv("cotizaciones_exportadas.csv", index=False)
    st.success("¡Cotizaciones exportadas correctamente!")

# Botón para futuras funcionalidades
if st.button("Próximas Funcionalidades"):
    st.info("¡Estamos trabajando en más funciones interactivas y avanzadas!")

# Información adicional para el usuario
st.sidebar.info("Para soporte técnico o dudas, contáctanos desde el menú superior.")
