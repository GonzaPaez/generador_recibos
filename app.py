import streamlit as st
from fpdf import FPDF
import os

st.set_page_config(page_title="Generador de Recibos de Sueldo")

# Crear carpeta si no existe
os.makedirs("pdfs", exist_ok=True)

# Inicializar la sesión de conceptos
if "conceptos" not in st.session_state:
    st.session_state["conceptos"] = []

st.title("🧾 Generador de Recibos de Sueldo")

st.markdown("Agregá uno a uno los conceptos (sueldos, adicionales, descuentos, etc.) que forman parte del recibo de sueldo.")

with st.form("form_concepto"):
    col1, col2 = st.columns(2)
    with col1:
        concepto = st.text_input("📝 Concepto (Ej: Sueldo básico)")
        cantidad = st.number_input("📌 Cantidad (días, horas, etc.)", min_value=0)
    with col2:
        remu = st.number_input("💵 Remunerativo", min_value=0.0, format="%.2f")
        no_remu = st.number_input("💸 No Remunerativo", min_value=0.0, format="%.2f")
        dedu = st.number_input("📉 Deducciones", min_value=0.0, format="%.2f")
    
    agregar = st.form_submit_button("➕ Agregar concepto")

    if agregar and concepto.strip() != "":
        st.session_state["conceptos"].append({
            "concepto": concepto,
            "cantidad": cantidad,
            "remu": remu,
            "no_remu": no_remu,
            "dedu": dedu
        })
        st.success(f"Concepto '{concepto}' agregado.")

st.divider()
st.subheader("📋 Conceptos cargados")

if st.session_state["conceptos"]:
    total_remu = total_norem = total_dedu = 0
    st.table([
        {
            "Concepto": c["concepto"],
            "Cant.": c["cantidad"],
            "Remunerativo": f"${c['remu']:,.2f}",
            "No Remunerativo": f"${c['no_remu']:,.2f}",
            "Deducciones": f"${c['dedu']:,.2f}"
        }
        for c in st.session_state["conceptos"]
    ])
else:
    st.info("Todavía no se ha cargado ningún concepto.")

st.divider()
st.subheader("📤 Generar Recibo PDF")

with st.form("generar_pdf"):
    col1, col2 = st.columns(2)
    with col1:
        empleado = st.text_input("👤 Nombre del empleado")
        legajo = st.text_input("🧾 Legajo")
    with col2:
        periodo = st.text_input("📅 Periodo (Ej: 08-2025)")
        cuil = st.text_input("🆔 CUIL")

    generar = st.form_submit_button("🖨️ Generar PDF")

    if generar:
        if empleado.strip() == "" or periodo.strip() == "":
            st.error("Faltan datos obligatorios (nombre o período).")
        elif not st.session_state["conceptos"]:
            st.error("Debe cargar al menos un concepto para generar el recibo.")
        else:
            filename = f"recibos/{empleado.replace(' ', '_')}_{periodo}.pdf"
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)

            # Encabezado
            pdf.cell(0, 5, "Empresa: Grupo Cinca S.A.                   CUIT: 30-00000000-0", ln=True)
            pdf.cell(0, 5, f"Empleado: {empleado}                       CUIL: {cuil}", ln=True)
            pdf.cell(0, 5, f"Legajo: {legajo}                           Periodo: {periodo}", ln=True)
            pdf.ln(5)

            # Tabla
            pdf.set_font("Helvetica", 'B', 9)
            headers = [("Concepto", 70), ("Cant.", 15), ("Remu", 30), ("No Remu", 30), ("Deducciones", 30)]
            for h, w in headers:
                pdf.cell(w, 6, h, border=1, align='C')
            pdf.ln()

            pdf.set_font("Helvetica", size=9)
            tot_r = tot_nr = tot_d = 0.0
            for c in st.session_state["conceptos"]:
                pdf.cell(70, 6, c["concepto"], border=1)
                pdf.cell(15, 6, str(c["cantidad"]), border=1, align='C')
                pdf.cell(30, 6, f"{c['remu']:,.2f}", border=1, align='R')
                pdf.cell(30, 6, f"{c['no_remu']:,.2f}", border=1, align='R')
                pdf.cell(30, 6, f"{c['dedu']:,.2f}", border=1, align='R')
                pdf.ln()
                tot_r += c["remu"]
                tot_nr += c["no_remu"]
                tot_d += c["dedu"]

            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(70, 6, "Totales", border=1)
            pdf.cell(15, 6, "", border=1)
            pdf.cell(30, 6, f"{tot_r:,.2f}", border=1, align='R')
            pdf.cell(30, 6, f"{tot_nr:,.2f}", border=1, align='R')
            pdf.cell(30, 6, f"{tot_d:,.2f}", border=1, align='R')
            pdf.ln(10)

            neto = tot_r + tot_nr - tot_d
            pdf.cell(0, 6, f"Sueldo Neto a Cobrar: ${neto:,.2f}", ln=True)
            pdf.ln(10)
            pdf.cell(0, 6, "_______________________________", ln=True)
            pdf.cell(0, 6, "Firma del Empleado", ln=True)

            os.makedirs("pdfs", exist_ok=True)
            pdf.output(filename)

            st.session_state["archivo_generado"] = filename
            st.success("Recibo generado correctamente.")

# Mostrar botón de descarga solo si ya se generó un recibo
if "archivo_generado" in st.session_state:
    with open(st.session_state["archivo_generado"], "rb") as f:
        st.download_button("📥 Descargar Recibo PDF", f, file_name=os.path.basename(st.session_state["archivo_generado"]))
