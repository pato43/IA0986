import streamlit as st
from datetime import datetime
from fpdf import FPDF

# Inicializar las variables de sesión si no están definidas
if "solicitudes" not in st.session_state:
    st.session_state["solicitudes"] = []  # Para solicitudes de presupuesto

if "presupuestos" not in st.session_state:
    st.session_state["presupuestos"] = []  # Para presupuestos aprobados

if "cotizaciones" not in st.session_state:
    st.session_state["cotizaciones"] = []  # Para cotizaciones

# Función para registrar solicitudes
def registrar_solicitudes():
    st.title("Registro de Solicitudes de Presupuesto para Holtmont Services( primer entremaniento de datos para IA especializada 1/20 )")
    with st.form("Formulario de Solicitud"):
        nombre = st.text_input("Nombre del Cliente:")
        descripcion = st.text_area("Descripción de la Solicitud:")
        presupuesto = st.number_input("Presupuesto Estimado:", min_value=0.0, step=0.1)
        fecha = st.date_input("Fecha de Solicitud:", value=datetime.today())
        
        submitted = st.form_submit_button("Registrar Solicitud")
        if submitted:
            if nombre and descripcion and presupuesto > 0:
                nueva_solicitud = {
                    "Nombre": nombre,
                    "Descripción": descripcion,
                    "Presupuesto": presupuesto,
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
# Función para generar reporte PDF
def generar_reporte_pdf():
    st.title("Generación de Reportes")
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
            st.success(f"Reporte generado exitosamente: {pdf_output_path}")
            with open(pdf_output_path, "rb") as file:
                st.download_button("Descargar Reporte PDF", file, file_name=pdf_output_path)
    else:
        st.warning("No hay presupuestos aprobados para generar un reporte.")

# Función para gestionar cotizaciones
def gestionar_cotizaciones():
    st.title("Gestión de Cotizaciones")
    if st.session_state["solicitudes"]:
        for idx, solicitud in enumerate(st.session_state["solicitudes"]):
            with st.expander(f"Solicitud {idx+1}: {solicitud['Nombre']}"):
                st.write("**Descripción:**", solicitud["Descripción"])
                st.write("**Presupuesto Estimado:**", solicitud["Presupuesto"])
                st.write("**Fecha:**", solicitud["Fecha"])
                
                # Inputs para registrar cotización
                proveedor = st.text_input(f"Nombre del Proveedor para Solicitud {idx+1}:", key=f"proveedor_{idx}")
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
                        st.success(f"Cotización registrada para la solicitud {idx+1}.")
                    else:
                        st.error("Por favor, completa todos los campos correctamente.")
    else:
        st.warning("No hay solicitudes registradas para gestionar cotizaciones.")

# Función para visualizar cotizaciones
def visualizar_cotizaciones():
    st.title("Visualización de Cotizaciones")
    if st.session_state["cotizaciones"]:
        for idx, cotizacion in enumerate(st.session_state["cotizaciones"]):
            with st.expander(f"Cotización {idx+1}: {cotizacion['Proveedor']}"):
                st.write("**Nombre del Cliente:**", cotizacion["Nombre Cliente"])
                st.write("**Proveedor:**", cotizacion["Proveedor"])
                st.write("**Costo Cotizado:**", cotizacion["Costo Cotizado"])
                st.write("**Detalles:**", cotizacion["Detalles"])
                st.write("**Fecha:**", cotizacion["Fecha"])
    else:
        st.warning("No hay cotizaciones registradas.")

# Navegación para la segunda parte
tab4, tab5, tab6 = st.tabs(["Generar Reportes", "Gestión de Cotizaciones", "Visualizar Cotizaciones"])

with tab4:
    generar_reporte_pdf()

with tab5:
    gestionar_cotizaciones()

with tab6:
    visualizar_cotizaciones()
