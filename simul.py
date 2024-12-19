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
    st.session_state["usuarios"] = []  # Para roles y restricciones

# Función para registrar solicitudes
def registrar_solicitudes():
    st.title("Registro de Solicitudes de Presupuesto para Holtmont Services")
    with st.form("Formulario de Solicitud"):
        nombre = st.text_input("Nombre del Cliente:")
        descripcion = st.text_area("Descripción de la Solicitud:")
        presupuesto = st.number_input("Presupuesto Estimado:", min_value=0.0, step=0.1)
        medio = st.selectbox("Medio de Solicitud:", ["En Campo", "Telefónica", "Correo Electrónico"])
        fecha = st.date_input("Fecha de Solicitud:", value=datetime.today())
        
        submitted = st.form_submit_button("Registrar Solicitud")
        if submitted:
            if nombre and descripcion and presupuesto > 0:
                nueva_solicitud = {
                    "Nombre": nombre,
                    "Descripción": descripcion,
                    "Presupuesto": presupuesto,
                    "Medio": medio,
                    "Fecha": fecha.strftime("%Y-%m-%d"),
                }
                st.session_state["solicitudes"].append(nueva_solicitud)
                st.success("Solicitud registrada exitosamente.")
            else:
                st.error("Por favor, completa todos los campos correctamente.")

# Función para visualizar solicitudes
def visualizar_solicitudes():
    st.title("Solicitudes de Presupuesto Registradas")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Presupuesto Estimado:**", solicitud["Presupuesto"])
                st.write("**Medio:**", solicitud["Medio"])
                st.write("**Fecha:**", solicitud["Fecha"])
    else:
        st.warning("No hay solicitudes registradas.")

# Función para aprobar presupuestos
def aprobar_presupuestos():
    st.title("Aprobación de Presupuestos")
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
                        st.success(f"Presupuesto aprobado para la solicitud {idx+1}.")
    else:
        st.warning("No hay solicitudes para aprobar.")

# Navegación entre tabs
tab1, tab2, tab3 = st.tabs(["Registrar Solicitudes", "Visualizar Solicitudes", "Aprobar Presupuestos"])

with tab1:
    registrar_solicitudes()

with tab2:
    visualizar_solicitudes()

with tab3:
    aprobar_presupuestos()
# Función para generar reportes automáticos con folios asignados
def generar_reportes_automaticos():
    st.title("Generación de Reportes Automáticos")
    if st.session_state["solicitudes"]:
        if st.button("Generar Reporte con Folios"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, txt="Reporte de Solicitudes Registradas", ln=True, align="C")
            pdf.ln(10)

            for idx, solicitud in enumerate(st.session_state["solicitudes"]):
                folio = f"FOLIO-{idx+1:04d}"
                pdf.cell(200, 10, txt=f"Folio: {folio}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Nombre: {solicitud['Nombre']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Descripción: {solicitud['Descripción']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Presupuesto Estimado: ${solicitud['Presupuesto']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Medio: {solicitud['Medio']}", ln=True, align="L")
                pdf.cell(200, 10, txt=f"Fecha: {solicitud['Fecha']}", ln=True, align="L")
                pdf.ln(5)
            
            # Guardar el PDF
            pdf_output_path = "reporte_solicitudes_folios.pdf"
            pdf.output(pdf_output_path)
            st.success(f"Reporte generado exitosamente: {pdf_output_path}")
            with open(pdf_output_path, "rb") as file:
                st.download_button("Descargar Reporte PDF con Folios", file, file_name=pdf_output_path)
    else:
        st.warning("No hay solicitudes registradas para generar reportes.")

# Función para gestionar roles y restricciones
def gestionar_roles():
    st.title("Gestión de Roles y Restricciones")
    with st.form("Formulario de Usuarios"):
        usuario = st.text_input("Nombre del Usuario:")
        rol = st.selectbox("Rol del Usuario:", ["Administrador", "Coordinador", "Campo", "Principal"])
        
        submitted = st.form_submit_button("Registrar Usuario")
        if submitted:
            if usuario and rol:
                nuevo_usuario = {"Usuario": usuario, "Rol": rol}
                st.session_state["usuarios"].append(nuevo_usuario)
                st.success("Usuario registrado exitosamente.")
            else:
                st.error("Por favor, completa todos los campos.")

    st.subheader("Usuarios Registrados")
    if st.session_state["usuarios"]:
        for idx, usuario in enumerate(st.session_state["usuarios"]):
            st.write(f"**Usuario {idx+1}:** {usuario['Usuario']} - **Rol:** {usuario['Rol']}")
    else:
        st.warning("No hay usuarios registrados.")

# Función para visualizar asignación de equipos y responsabilidades
def visualizar_equipos():
    st.title("Asignación de Equipos y Responsabilidades")
    equipos = [
        {"Equipo": "Equipo A", "Responsable": "Líder A", "Proyectos Asignados": 5},
        {"Equipo": "Equipo B", "Responsable": "Líder B", "Proyectos Asignados": 3},
    ]
    for equipo in equipos:
        with st.expander(f"{equipo['Equipo']} - Responsable: {equipo['Responsable']}"):
            st.write(f"**Proyectos Asignados:** {equipo['Proyectos Asignados']}")

# Navegación para esta sección
tab4, tab5, tab6 = st.tabs(["Generar Reportes con Folios", "Gestión de Roles", "Visualización de Equipos"])

with tab4:
    generar_reportes_automaticos()

with tab5:
    gestionar_roles()

with tab6:
    visualizar_equipos()
# Función para tiempos de respuesta y sistema de semáforos
def gestionar_tiempos_respuesta():
    st.title("Gestión de Tiempos de Respuesta")
    dias_alerta = st.slider("Definir días para alertas:", min_value=1, max_value=10, value=3)
    
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            fecha_solicitud = datetime.strptime(solicitud["Fecha"], "%Y-%m-%d")
            dias_transcurridos = (datetime.today() - fecha_solicitud).days
            
            estado = "En Tiempo"
            color = "green"
            if dias_transcurridos > dias_alerta:
                estado = "Retrasado"
                color = "red"
            elif dias_transcurridos > dias_alerta - 2:
                estado = "Cercano a Límite"
                color = "yellow"
            
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Días Transcurridos:**", dias_transcurridos)
                st.markdown(f"**Estado:** <span style='color:{color}'>{estado}</span>", unsafe_allow_html=True)
    else:
        st.warning("No hay solicitudes registradas para gestionar tiempos de respuesta.")

# Función para monitoreo y asignación de proyectos
def monitorear_asignaciones():
    st.title("Monitoreo y Asignación de Proyectos")
    if st.session_state["presupuestos"]:
        for idx, presupuesto in enumerate(st.session_state["presupuestos"]):
            with st.expander(f"Proyecto {idx+1}: {presupuesto['Nombre']}"):
                st.write("**Descripción:**", presupuesto["Descripción"])
                st.write("**Presupuesto Aprobado:**", presupuesto["Presupuesto Aprobado"])
                st.write("**Fecha:**", presupuesto["Fecha"])
                
                asignado_a = st.text_input(f"Asignar Responsable para Proyecto {idx+1}:", key=f"responsable_{idx}")
                progreso = st.slider(f"Progreso del Proyecto {idx+1}:", 0, 100, key=f"progreso_{idx}")
                
                if st.button(f"Actualizar Proyecto {idx+1}", key=f"actualizar_{idx}"):
                    st.success(f"Proyecto {idx+1} actualizado: Responsable: {asignado_a}, Progreso: {progreso}%")
    else:
        st.warning("No hay proyectos aprobados para monitorear.")

# Función para generar alertas y recordatorios
def generar_alertas():
    st.title("Alertas y Recordatorios")
    recordatorios = [
        {"Tarea": "Enviar cotización al cliente", "Fecha Límite": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")},
        {"Tarea": "Revisión de presupuesto", "Fecha Límite": (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")},
    ]
    for idx, recordatorio in enumerate(recordatorios):
        with st.expander(f"Recordatorio {idx+1}: {recordatorio['Tarea']}"):
            st.write("**Fecha Límite:**", recordatorio["Fecha Límite"])

# Navegación para esta última sección
tab7, tab8, tab9 = st.tabs(["Tiempos de Respuesta", "Monitoreo de Asignaciones", "Alertas y Recordatorios"])

with tab7:
    gestionar_tiempos_respuesta()

with tab8:
    monitorear_asignaciones()

with tab9:
    generar_alertas()
