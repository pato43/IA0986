import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF

# Inicializar las variables de sesión si no están definidas
if "solicitudes" not in st.session_state:
    st.session_state["solicitudes"] = []  # Para solicitudes de presupuesto

if "presupuestos" not in st.session_state:
    st.session_state["presupuestos"] = []  # Para presupuestos aprobados

if "cotizaciones" not in st.session_state:
    st.session_state["cotizaciones"] = []  # Para cotizaciones

if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = []  # Para gestión de usuarios

# Configuración del layout principal
st.set_page_config(
    page_title="Dashboard Holtmont Services",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Barra lateral de navegación
with st.sidebar:
    st.title("📊 Holtmont Dashboard")
    st.markdown("Navega por las diferentes secciones:")
    section = st.radio("Secciones", [
        "Registrar Solicitudes",
        "Visualizar Solicitudes",
        "Aprobar Presupuestos",
        "Gestión de Cotizaciones",
        "Visualización de Cotizaciones",
        "Tiempos de Respuesta",
        "Asignación de Proyectos",
        "Alertas y Recordatorios",
        "Roles y Equipos"
    ])
    st.markdown("---")
    st.info("Demo para el primer entrenamiento de IA especializada (1/20)")

# Función para registrar solicitudes
def registrar_solicitudes():
    st.title("📌 Registro de Solicitudes")
    st.markdown("Ingresa los detalles para registrar una nueva solicitud de presupuesto.")
    with st.form("Formulario de Solicitud"):
        nombre = st.text_input("Nombre del Cliente:")
        descripcion = st.text_area("Descripción de la Solicitud:")
        presupuesto = st.number_input("Presupuesto Estimado:", min_value=0.0, step=0.1)
        fecha = st.date_input("Fecha de Solicitud:", value=datetime.today())
        medio = st.selectbox("Medio de Solicitud:", ["Campo", "Teléfono", "Correo Electrónico"])
        
        submitted = st.form_submit_button("Registrar Solicitud")
        if submitted:
            if nombre and descripcion and presupuesto > 0:
                nueva_solicitud = {
                    "Nombre": nombre,
                    "Descripción": descripcion,
                    "Presupuesto": presupuesto,
                    "Fecha": fecha.strftime("%Y-%m-%d"),
                    "Medio": medio
                }
                st.session_state["solicitudes"].append(nueva_solicitud)
                st.success("✅ Solicitud registrada exitosamente.")
            else:
                st.error("⚠️ Por favor, completa todos los campos correctamente.")

# Función para visualizar solicitudes
def visualizar_solicitudes():
    st.title("📋 Visualización de Solicitudes")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Presupuesto Estimado:**", solicitud["Presupuesto"])
                st.write("**Fecha:**", solicitud["Fecha"])
                st.write("**Medio:**", solicitud["Medio"])
    else:
        st.warning("⚠️ No hay solicitudes registradas.")

# Función para aprobar presupuestos
def aprobar_presupuestos():
    st.title("✅ Aprobación de Presupuestos")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Presupuesto Estimado:**", solicitud["Presupuesto"])
                st.write("**Fecha:**", solicitud["Fecha"])
                
                presupuesto_aprobado = st.number_input(f"Presupuesto Aprobado para {solicitud['Nombre']}:",
                                                       min_value=0.0, step=0.1, key=f"presupuesto_aprobado_{idx}")
                if st.button(f"Aprobar Solicitud {idx+1}", key=f"aprobar_solicitud_{idx}"):
                    if presupuesto_aprobado > 0:
                        nuevo_presupuesto = {
                            "Nombre": solicitud["Nombre"],
                            "Descripción": solicitud["Descripción"],
                            "Presupuesto Aprobado": presupuesto_aprobado,
                            "Fecha": solicitud["Fecha"],
                        }
                        st.session_state["presupuestos"].append(nuevo_presupuesto)
                        st.success(f"✅ Presupuesto aprobado para la solicitud {idx+1}.")
    else:
        st.warning("⚠️ No hay solicitudes para aprobar.")

# Lógica para renderizar la sección seleccionada
if section == "Registrar Solicitudes":
    registrar_solicitudes()
elif section == "Visualizar Solicitudes":
    visualizar_solicitudes()
elif section == "Aprobar Presupuestos":
    aprobar_presupuestos()
# Función para gestionar cotizaciones
def gestionar_cotizaciones():
    st.title("📄 Gestión de Cotizaciones")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Presupuesto Estimado:**", solicitud["Presupuesto"])
                st.write("**Fecha:**", solicitud["Fecha"])
                st.write("**Medio:**", solicitud["Medio"])
                
                proveedor = st.text_input(f"Proveedor para Solicitud {idx+1}:", key=f"proveedor_{idx}")
                costo = st.number_input(f"Costo Cotizado para Solicitud {idx+1}:", min_value=0.0, step=0.1, key=f"costo_{idx}")
                detalles = st.text_area(f"Detalles de la Cotización para Solicitud {idx+1}:", key=f"detalles_{idx}")
                
                if st.button(f"Registrar Cotización {idx+1}", key=f"registrar_cot_{idx}"):
                    if proveedor and costo > 0 and detalles:
                        nueva_cotizacion = {
                            "Nombre Cliente": solicitud["Nombre"],
                            "Proveedor": proveedor,
                            "Costo Cotizado": costo,
                            "Detalles": detalles,
                            "Fecha": solicitud["Fecha"]
                        }
                        st.session_state["cotizaciones"].append(nueva_cotizacion)
                        st.success(f"✅ Cotización registrada para la solicitud {idx+1}.")
                    else:
                        st.error("⚠️ Por favor, completa todos los campos correctamente.")
    else:
        st.warning("⚠️ No hay solicitudes registradas para gestionar cotizaciones.")

# Función para visualizar cotizaciones
def visualizar_cotizaciones():
    st.title("📊 Visualización de Cotizaciones")
    if st.session_state["cotizaciones"]:
        for idx, cotizacion in enumerate(st.session_state["cotizaciones"]):
            with st.expander(f"Cotización {idx+1}: {cotizacion['Proveedor']}"):
                st.write("**Cliente:**", cotizacion["Nombre Cliente"])
                st.write("**Proveedor:**", cotizacion["Proveedor"])
                st.write("**Costo Cotizado:**", cotizacion["Costo Cotizado"])
                st.write("**Detalles:**", cotizacion["Detalles"])
                st.write("**Fecha:**", cotizacion["Fecha"])
    else:
        st.warning("⚠️ No hay cotizaciones registradas.")

# Función para generar reportes PDF
def generar_reporte_pdf():
    st.title("📑 Generación de Reportes PDF")
    if st.session_state["presupuestos"]:
        if st.button("Generar Reporte PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Reporte de Presupuestos Aprobados", ln=True, align="C")
            pdf.ln(10)

            for idx, presupuesto in enumerate(st.session_state["presupuestos"]):
                pdf.cell(200, 10, txt=f"Presupuesto {idx+1}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Nombre: {presupuesto['Nombre']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Descripción: {presupuesto['Descripción']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Presupuesto Aprobado: ${presupuesto['Presupuesto Aprobado']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Fecha: {presupuesto['Fecha']}", ln=True, align="L")
                pdf.ln(5)
            
            # Guardar el PDF
            pdf_output_path = "reporte_presupuestos.pdf"
            pdf.output(pdf_output_path)
            st.success(f"✅ Reporte generado exitosamente: {pdf_output_path}")
            with open(pdf_output_path, "rb") as file:
                st.download_button("Descargar Reporte PDF", file, file_name=pdf_output_path)
    else:
        st.warning("⚠️ No hay presupuestos aprobados para generar un reporte.")

# Lógica para renderizar la sección seleccionada
if section == "Gestión de Cotizaciones":
    gestionar_cotizaciones()
elif section == "Visualización de Cotizaciones":
    visualizar_cotizaciones()
elif section == "Generar Reportes PDF":
    generar_reporte_pdf()
# Función para gestionar tiempos de respuesta y semáforos
def gestionar_tiempos():
    st.title("⏳ Gestión de Tiempos de Respuesta")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            tiempo_respuesta = st.number_input(
                f"Días estimados de respuesta para Solicitud {idx+1}:",
                min_value=0, max_value=30, step=1, key=f"tiempo_respuesta_{idx}"
            )
            if tiempo_respuesta > 0:
                color = "🟢" if tiempo_respuesta <= 2 else "🟡" if tiempo_respuesta <= 5 else "🔴"
                st.write(f"Estado de tiempo para la Solicitud {idx+1}: {color}")
    else:
        st.warning("⚠️ No hay solicitudes registradas para gestionar tiempos de respuesta.")

# Función para gestionar asignaciones y equipos
def gestionar_asignaciones():
    st.title("📌 Gestión de Asignaciones")
    if st.session_state["presupuestos"]:
        for idx, presupuesto in enumerate(st.session_state["presupuestos"]):
            with st.expander(f"Presupuesto {idx+1}: {presupuesto['Nombre']}"):
                equipo_asignado = st.text_input(
                    f"Equipo asignado para Presupuesto {idx+1}:",
                    key=f"equipo_asignado_{idx}"
                )
                responsabilidades = st.text_area(
                    f"Responsabilidades asignadas para el Equipo {equipo_asignado}:",
                    key=f"responsabilidades_{idx}"
                )
                if st.button(f"Asignar Equipo a Presupuesto {idx+1}", key=f"asignar_equipo_{idx}"):
                    if equipo_asignado and responsabilidades:
                        st.success(f"✅ Equipo '{equipo_asignado}' asignado exitosamente.")
                    else:
                        st.error("⚠️ Por favor, completa los campos de asignación.")
    else:
        st.warning("⚠️ No hay presupuestos aprobados para asignar equipos.")

# Función para gestionar alertas y recordatorios
def gestionar_alertas():
    st.title("⏰ Alertas y Recordatorios Automáticos")
    alertas_pendientes = []
    for solicitud in st.session_state["solicitudes"]:
        fecha_solicitud = datetime.strptime(solicitud["Fecha"], "%Y-%m-%d")
        dias_transcurridos = (datetime.today() - fecha_solicitud).days
        if dias_transcurridos > 5:
            alertas_pendientes.append(
                f"⚠️ Solicitud de {solicitud['Nombre']} está pendiente por más de {dias_transcurridos} días."
            )
    if alertas_pendientes:
        for alerta in alertas_pendientes:
            st.warning(alerta)
    else:
        st.success("✅ No hay alertas pendientes.")

# Dashboards personalizados por roles
def dashboard_personalizado(usuario):
    if usuario == "Administrativo":
        gestionar_asignaciones()
        generar_reporte_pdf()
    elif usuario == "Coordinador":
        gestionar_tiempos()
        gestionar_alertas()
    elif usuario == "Campo":
        gestionar_cotizaciones()
    else:
        st.warning("⚠️ Rol no reconocido. Selecciona un rol válido.")

# Función principal para seleccionar el rol del usuario
def seleccionar_rol_usuario():
    st.sidebar.title("🎭 Selección de Rol de Usuario")
    usuario = st.sidebar.selectbox(
        "Selecciona tu rol:", ["Seleccione", "Administrativo", "Coordinador", "Campo"]
    )
    if usuario != "Seleccione":
        dashboard_personalizado(usuario)

# Inicio del programa principal
def main():
    seleccionar_rol_usuario()

if __name__ == "__main__":
    main()
