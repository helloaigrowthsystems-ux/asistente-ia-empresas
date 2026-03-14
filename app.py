import streamlit as st
import os
import json
import re
import pandas as pd
from io import BytesIO
from file_handler import extraer_texto_pdf, extraer_texto_excel
from ai_processor import procesar_documento, procesar_pregunta
from generador import generar_contrato, generar_presupuesto, generar_informe
from chatbot import chatbot_responder
from exportador import exportar_pdf, exportar_docx
from auth import mostrar_login, cerrar_sesion, mostrar_uso_sidebar, puede_usar, registrar_uso

st.set_page_config(page_title="IA para Empresas", page_icon="🤖", layout="wide")

# =====================
# LOGIN
# =====================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    mostrar_login()
    st.stop()

# ─── Componente reutilizable de descarga ──────────────────────────────────────

def botones_descarga(contenido: str, tipo_doc: str, metadata: dict = None, nombre_base: str = "documento"):
    st.markdown("---")
    st.caption("📥 Descargar documento:")
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            pdf_bytes = exportar_pdf(contenido, tipo_doc=tipo_doc, metadata=metadata)
            st.download_button(
                label="📄 Descargar PDF",
                data=pdf_bytes,
                file_name=f"{nombre_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error PDF: {e}")

    with col2:
        try:
            docx_bytes = exportar_docx(contenido, tipo_doc=tipo_doc, metadata=metadata)
            st.download_button(
                label="📝 Descargar Word",
                data=docx_bytes,
                file_name=f"{nombre_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error DOCX: {e}")

    with col3:
        st.download_button(
            label="📋 Descargar TXT",
            data=contenido,
            file_name=f"{nombre_base}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# =====================
# SIDEBAR
# =====================
st.sidebar.title("🧩 Módulos")
mostrar_uso_sidebar()

modulo = st.sidebar.radio("Elige un módulo:", [
    "📄 Procesar documentos",
    "✍️ Generar documentos",
    "💬 Chatbot personalizado",
])

st.title("🤖 Asistente IA para Empresas")
st.caption("Tu plataforma completa de inteligencia artificial para empresas")

# =====================
# MÓDULO 1: PROCESAR
# =====================
if modulo == "📄 Procesar documentos":
    st.subheader("📄 Procesar documentos con IA")
    st.caption("Extrae datos de facturas, contratos y cualquier documento")

    modo = st.radio("¿Qué quieres hacer?", [
        "📊 Extraer datos estructurados",
        "💬 Hacer preguntas al documento",
        "📝 Resumir documento"
    ], horizontal=True)

    archivo = st.file_uploader("Sube tu documento", type=["pdf", "xlsx", "xls"])

    if archivo:
        ext = archivo.name.split(".")[-1]
        ruta_temp = f"temp.{ext}"
        with open(ruta_temp, "wb") as f:
            f.write(archivo.read())

        if ext == "pdf":
            texto = extraer_texto_pdf(ruta_temp)
        else:
            texto = extraer_texto_excel(ruta_temp)

        st.success(f"✅ Documento cargado: {archivo.name}")

        if modo == "📊 Extraer datos estructurados":
            ejemplos = st.selectbox("Ejemplos rápidos:", [
                "Personalizado...",
                "Extrae: proveedor, fecha, importe total, número de factura",
                "Extrae: nombre del cliente, dirección, teléfono, email",
                "Extrae: partes del contrato, fecha de firma, duración, importe",
                "Extrae: producto, cantidad, precio unitario, total"
            ])
            instruccion = st.text_input("Escribe tu instrucción:") if ejemplos == "Personalizado..." else ejemplos

            if st.button("🚀 Extraer con IA") and instruccion:
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Procesando..."):
                        resultado = procesar_documento(texto, instruccion)
                    registrar_uso()
                    st.code(resultado, language="json")
                    try:
                        texto_limpio = re.sub(r"```json|```", "", resultado).strip()
                        datos = json.loads(texto_limpio)
                        if isinstance(datos, dict):
                            datos = [datos]
                        df = pd.DataFrame(datos)
                        buffer = BytesIO()
                        df.to_excel(buffer, index=False)
                        buffer.seek(0)
                        st.download_button(
                            "📥 Descargar Excel",
                            data=buffer,
                            file_name="resultado.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception:
                        st.info("💡 El resultado no es JSON puro, no se puede exportar a Excel.")

        elif modo == "💬 Hacer preguntas al documento":
            pregunta = st.text_input("Tu pregunta:", placeholder="¿Cuál es el importe total?")
            if st.button("💬 Preguntar") and pregunta:
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Pensando..."):
                        respuesta = procesar_pregunta(texto, pregunta)
                    registrar_uso()
                    st.write(respuesta)
                    if respuesta:
                        botones_descarga(
                            contenido=f"Pregunta: {pregunta}\n\nRespuesta:\n{respuesta}",
                            tipo_doc="informe",
                            nombre_base="respuesta_documento"
                        )

        elif modo == "📝 Resumir documento":
            if st.button("📝 Generar resumen"):
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Resumiendo..."):
                        resumen = procesar_pregunta(texto, "Haz un resumen ejecutivo claro y estructurado.")
                    registrar_uso()
                    st.write(resumen)
                    if resumen:
                        botones_descarga(
                            contenido=resumen,
                            tipo_doc="informe",
                            nombre_base="resumen_documento"
                        )

        os.remove(ruta_temp)
    else:
        st.info("👆 Sube un documento para empezar")

# =====================
# MÓDULO 2: GENERAR
# =====================
elif modulo == "✍️ Generar documentos":
    st.subheader("✍️ Generador de documentos con IA")
    st.caption("Genera contratos, presupuestos e informes en segundos")

    tipo_doc = st.radio("¿Qué quieres generar?", [
        "📋 Contrato", "💰 Presupuesto", "📊 Informe ejecutivo"
    ], horizontal=True)

    if tipo_doc == "📋 Contrato":
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de contrato:", ["Servicios", "Trabajo", "Alquiler", "Compraventa", "Confidencialidad"])
            proveedor = st.text_input("Empresa/Proveedor:")
            cliente = st.text_input("Cliente:")
        with col2:
            servicio = st.text_input("Servicio o descripción:")
            importe = st.text_input("Importe:")
            duracion = st.text_input("Duración:", placeholder="6 meses")
            fecha_inicio = st.text_input("Fecha de inicio:", placeholder="01/04/2026")

        if st.button("📋 Generar contrato"):
            if proveedor and cliente and servicio:
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Generando contrato con IA..."):
                        resultado = generar_contrato({
                            "tipo": tipo, "proveedor": proveedor, "cliente": cliente,
                            "servicio": servicio, "importe": importe,
                            "duracion": duracion, "fecha_inicio": fecha_inicio
                        })
                    registrar_uso()
                    st.subheader("📋 Contrato generado:")
                    st.text_area("", resultado, height=400)
                    botones_descarga(
                        contenido=resultado,
                        tipo_doc="contrato",
                        metadata={"empresa": proveedor, "cliente": cliente, "fecha": fecha_inicio},
                        nombre_base=f"contrato_{cliente.replace(' ', '_') if cliente else 'nuevo'}"
                    )
            else:
                st.warning("Rellena al menos proveedor, cliente y servicio.")

    elif tipo_doc == "💰 Presupuesto":
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Tu empresa:")
            cliente = st.text_input("Cliente:")
        with col2:
            validez = st.text_input("Validez:", placeholder="30 días")
            fecha = st.text_input("Fecha:", placeholder="14/03/2026")
        servicios = st.text_area(
            "Servicios/Productos y precios:",
            placeholder="Desarrollo web: 2000€\nMantenimiento mensual: 200€\nFormación: 500€"
        )

        if st.button("💰 Generar presupuesto"):
            if empresa and cliente and servicios:
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Generando presupuesto con IA..."):
                        resultado = generar_presupuesto({
                            "empresa": empresa, "cliente": cliente,
                            "servicios": servicios, "validez": validez, "fecha": fecha
                        })
                    registrar_uso()
                    st.subheader("💰 Presupuesto generado:")
                    st.text_area("", resultado, height=400)
                    botones_descarga(
                        contenido=resultado,
                        tipo_doc="presupuesto",
                        metadata={"empresa": empresa, "cliente": cliente, "fecha": fecha},
                        nombre_base=f"presupuesto_{cliente.replace(' ', '_') if cliente else 'nuevo'}"
                    )
            else:
                st.warning("Rellena empresa, cliente y servicios.")

    elif tipo_doc == "📊 Informe ejecutivo":
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa:")
            tema = st.text_input("Tema del informe:", placeholder="Ventas Q1 2026")
        with col2:
            periodo = st.text_input("Período:", placeholder="Enero - Marzo 2026")
        datos = st.text_area(
            "Datos clave:",
            placeholder="Ventas totales: 150.000€\nClientes nuevos: 23\nTicket medio: 6.500€"
        )

        if st.button("📊 Generar informe"):
            if empresa and tema and datos:
                ok, msg = puede_usar()
                if not ok:
                    st.error(msg)
                else:
                    with st.spinner("Generando informe con IA..."):
                        resultado = generar_informe({
                            "empresa": empresa, "tema": tema,
                            "periodo": periodo, "datos": datos
                        })
                    registrar_uso()
                    st.subheader("📊 Informe generado:")
                    st.text_area("", resultado, height=400)
                    botones_descarga(
                        contenido=resultado,
                        tipo_doc="informe",
                        metadata={"empresa": empresa, "fecha": periodo},
                        nombre_base=f"informe_{tema.replace(' ', '_') if tema else 'nuevo'}"
                    )
            else:
                st.warning("Rellena empresa, tema y datos.")

# =====================
# MÓDULO 3: CHATBOT
# =====================
elif modulo == "💬 Chatbot personalizado":
    st.subheader("💬 Chatbot personalizado con IA")
    st.caption("Entrena un chatbot con la información de tu empresa")

    with st.expander("⚙️ Configurar información de la empresa", expanded=True):
        info_empresa = st.text_area(
            "Pega aquí toda la información de tu empresa:",
            height=200,
            placeholder="""Empresa: Tech Solutions S.L.
Servicios: Desarrollo web, apps móviles, consultoría IA
Precios: Desde 1.500€ por proyecto
Horario: Lunes a Viernes 9:00 - 18:00
Contacto: info@techsolutions.com"""
        )

    if info_empresa:
        st.success("✅ Chatbot configurado y listo")
        st.subheader("🤖 Chat")

        if "historial_chat" not in st.session_state:
            st.session_state.historial_chat = []

        for mensaje in st.session_state.historial_chat:
            if mensaje["role"] == "user":
                st.chat_message("user").write(mensaje["content"])
            else:
                st.chat_message("assistant").write(mensaje["content"])

        pregunta = st.chat_input("Escribe tu pregunta...")

        if pregunta:
            ok, msg = puede_usar()
            if not ok:
                st.error(msg)
            else:
                st.chat_message("user").write(pregunta)
                with st.spinner("Pensando..."):
                    respuesta = chatbot_responder(
                        st.session_state.historial_chat,
                        info_empresa,
                        pregunta
                    )
                registrar_uso()
                st.chat_message("assistant").write(respuesta)
                st.session_state.historial_chat.append({"role": "user", "content": pregunta})
                st.session_state.historial_chat.append({"role": "assistant", "content": respuesta})

        col_limpiar, col_exportar = st.columns([1, 2])
        with col_limpiar:
            if st.button("🗑️ Limpiar conversación"):
                st.session_state.historial_chat = []
                st.rerun()

        if st.session_state.get("historial_chat"):
            with col_exportar:
                if st.button("📥 Exportar conversación"):
                    transcript = "\n\n".join([
                        f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                        for m in st.session_state.historial_chat
                    ])
                    st.session_state["transcript_export"] = transcript

            if st.session_state.get("transcript_export"):
                botones_descarga(
                    contenido=st.session_state["transcript_export"],
                    tipo_doc="informe",
                    nombre_base="conversacion_chatbot"
                )
    else:
        st.info("👆 Configura la información de tu empresa para activar el chatbot")