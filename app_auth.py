# app.py — versión con autenticación
# Sustituye tu app.py actual por este archivo

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
from auth import mostrar_login, mostrar_uso_sidebar, puede_usar, registrar_uso

st.set_page_config(page_title="IA para Empresas", page_icon="🤖", layout="wide")

# ─── Guard de autenticación ───────────────────────────────────────────────────
if "usuario" not in st.session_state:
    mostrar_login()
    st.stop()

# ─── App principal ────────────────────────────────────────────────────────────
st.title("🤖 Asistente IA para Empresas")
st.caption("Tu plataforma completa de inteligencia artificial para empresas")

st.sidebar.title("🧩 Módulos")
modulo = st.sidebar.radio("Elige un módulo:", [
    "📄 Procesar documentos",
    "✍️ Generar documentos",
    "💬 Chatbot personalizado",
])
mostrar_uso_sidebar()

def botones_descarga(contenido, tipo_doc, metadata=None, nombre_base="documento"):
    st.markdown("---")
    st.caption("📥 Descargar documento:")
    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            pdf_bytes = exportar_pdf(contenido, tipo_doc=tipo_doc, metadata=metadata)
            st.download_button("📄 PDF", data=pdf_bytes, file_name=f"{nombre_base}.pdf",
                mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Error PDF: {e}")
    with col2:
        try:
            docx_bytes = exportar_docx(contenido, tipo_doc=tipo_doc, metadata=metadata)
            st.download_button("📝 Word", data=docx_bytes, file_name=f"{nombre_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
        except Exception as e:
            st.error(f"Error DOCX: {e}")
    with col3:
        st.download_button("📋 TXT", data=contenido, file_name=f"{nombre_base}.txt",
            mime="text/plain", use_container_width=True)

def check_y_usar():
    ok, msg = puede_usar()
    if not ok:
        st.warning(f"⚠️ {msg}")
        st.info("📩 Escríbenos para activar el plan Pro.")
        return False
    registrar_uso()
    return True

# MÓDULO 1: PROCESAR
if modulo == "📄 Procesar documentos":
    st.subheader("📄 Procesar documentos con IA")
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
        texto = extraer_texto_pdf(ruta_temp) if ext == "pdf" else extraer_texto_excel(ruta_temp)
        st.success(f"✅ Documento cargado: {archivo.name}")
        if modo == "📊 Extraer datos estructurados":
            ejemplos = st.selectbox("Ejemplos rápidos:", [
                "Personalizado...",
                "Extrae: proveedor, fecha, importe total, número de factura",
                "Extrae: nombre del cliente, dirección, teléfono, email",
            ])
            instruccion = st.text_input("Escribe tu instrucción:") if ejemplos == "Personalizado..." else ejemplos
            if st.button("🚀 Extraer con IA") and instruccion:
                if check_y_usar():
                    with st.spinner("Procesando..."):
                        resultado = procesar_documento(texto, instruccion)
                    st.code(resultado, language="json")
                    try:
                        datos = json.loads(re.sub(r"```json|```", "", resultado).strip())
                        if isinstance(datos, dict): datos = [datos]
                        df = pd.DataFrame(datos)
                        buf = BytesIO(); df.to_excel(buf, index=False); buf.seek(0)
                        st.download_button("📥 Excel", data=buf, file_name="resultado.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    except Exception:
                        st.info("El resultado no es JSON exportable.")
        elif modo == "💬 Hacer preguntas al documento":
            pregunta = st.text_input("Tu pregunta:")
            if st.button("💬 Preguntar") and pregunta:
                if check_y_usar():
                    with st.spinner("Pensando..."): respuesta = procesar_pregunta(texto, pregunta)
                    st.write(respuesta)
                    botones_descarga(f"Pregunta: {pregunta}\n\nRespuesta:\n{respuesta}",
                        "informe", nombre_base="respuesta")
        elif modo == "📝 Resumir documento":
            if st.button("📝 Generar resumen"):
                if check_y_usar():
                    with st.spinner("Resumiendo..."):
                        resumen = procesar_pregunta(texto, "Haz un resumen ejecutivo claro y estructurado.")
                    st.write(resumen)
                    botones_descarga(resumen, "informe", nombre_base="resumen")
        os.remove(ruta_temp)
    else:
        st.info("👆 Sube un documento para empezar")

# MÓDULO 2: GENERAR
elif modulo == "✍️ Generar documentos":
    st.subheader("✍️ Generador de documentos con IA")
    tipo_doc = st.radio("¿Qué quieres generar?", ["📋 Contrato", "💰 Presupuesto", "📊 Informe ejecutivo"], horizontal=True)
    if tipo_doc == "📋 Contrato":
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo:", ["Servicios", "Trabajo", "Alquiler", "Compraventa", "Confidencialidad"])
            proveedor = st.text_input("Empresa/Proveedor:")
            cliente = st.text_input("Cliente:")
        with col2:
            servicio = st.text_input("Servicio:")
            importe = st.text_input("Importe:")
            duracion = st.text_input("Duración:", placeholder="6 meses")
            fecha_inicio = st.text_input("Fecha inicio:", placeholder="01/04/2026")
        if st.button("📋 Generar contrato"):
            if proveedor and cliente and servicio:
                if check_y_usar():
                    with st.spinner("Generando..."): resultado = generar_contrato({"tipo": tipo, "proveedor": proveedor, "cliente": cliente, "servicio": servicio, "importe": importe, "duracion": duracion, "fecha_inicio": fecha_inicio})
                    st.text_area("", resultado, height=400)
                    botones_descarga(resultado, "contrato", {"empresa": proveedor, "cliente": cliente, "fecha": fecha_inicio}, f"contrato_{cliente.replace(' ','_')}")
            else: st.warning("Rellena proveedor, cliente y servicio.")
    elif tipo_doc == "💰 Presupuesto":
        col1, col2 = st.columns(2)
        with col1: empresa = st.text_input("Tu empresa:"); cliente = st.text_input("Cliente:")
        with col2: validez = st.text_input("Validez:", placeholder="30 días"); fecha = st.text_input("Fecha:", placeholder="14/03/2026")
        servicios = st.text_area("Servicios y precios:", placeholder="Desarrollo web: 2000€")
        if st.button("💰 Generar presupuesto"):
            if empresa and cliente and servicios:
                if check_y_usar():
                    with st.spinner("Generando..."): resultado = generar_presupuesto({"empresa": empresa, "cliente": cliente, "servicios": servicios, "validez": validez, "fecha": fecha})
                    st.text_area("", resultado, height=400)
                    botones_descarga(resultado, "presupuesto", {"empresa": empresa, "cliente": cliente, "fecha": fecha}, f"presupuesto_{cliente.replace(' ','_')}")
            else: st.warning("Rellena empresa, cliente y servicios.")
    elif tipo_doc == "📊 Informe ejecutivo":
        col1, col2 = st.columns(2)
        with col1: empresa = st.text_input("Empresa:"); tema = st.text_input("Tema:", placeholder="Ventas Q1 2026")
        with col2: periodo = st.text_input("Período:", placeholder="Enero - Marzo 2026")
        datos = st.text_area("Datos clave:", placeholder="Ventas: 150.000€\nClientes: 23")
        if st.button("📊 Generar informe"):
            if empresa and tema and datos:
                if check_y_usar():
                    with st.spinner("Generando..."): resultado = generar_informe({"empresa": empresa, "tema": tema, "periodo": periodo, "datos": datos})
                    st.text_area("", resultado, height=400)
                    botones_descarga(resultado, "informe", {"empresa": empresa, "fecha": periodo}, f"informe_{tema.replace(' ','_')}")
            else: st.warning("Rellena empresa, tema y datos.")

# MÓDULO 3: CHATBOT
elif modulo == "💬 Chatbot personalizado":
    st.subheader("💬 Chatbot personalizado con IA")
    with st.expander("⚙️ Configurar empresa", expanded=True):
        info_empresa = st.text_area("Información de tu empresa:", height=200,
            placeholder="Empresa: Tech Solutions\nServicios: Desarrollo web\nPrecios: Desde 1.500€")
    if info_empresa:
        st.success("✅ Chatbot listo")
        if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
        for m in st.session_state.historial_chat:
            st.chat_message(m["role"]).write(m["content"])
        pregunta = st.chat_input("Escribe tu pregunta...")
        if pregunta:
            st.chat_message("user").write(pregunta)
            if check_y_usar():
                with st.spinner("Pensando..."): respuesta = chatbot_responder(st.session_state.historial_chat, info_empresa, pregunta)
                st.chat_message("assistant").write(respuesta)
                st.session_state.historial_chat += [{"role": "user", "content": pregunta}, {"role": "assistant", "content": respuesta}]
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🗑️ Limpiar"): st.session_state.historial_chat = []; st.rerun()
        if st.session_state.get("historial_chat"):
            with col2:
                if st.button("📥 Exportar"):
                    st.session_state["transcript"] = "\n\n".join([f"{'Usuario' if m['role']=='user' else 'Asistente'}: {m['content']}" for m in st.session_state.historial_chat])
            if st.session_state.get("transcript"):
                botones_descarga(st.session_state["transcript"], "informe", nombre_base="conversacion")
    else:
        st.info("👆 Configura la información de tu empresa para activar el chatbot")