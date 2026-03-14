import streamlit as st
import os
import json
import re
import pandas as pd
from io import BytesIO
from file_handler import extraer_texto_pdf, extraer_texto_excel
from ai_processor import procesar_documento, procesar_pregunta
from generador import generar_contrato, generar_presupuesto, generar_informe

st.set_page_config(page_title="IA para Empresas", page_icon="🤖", layout="wide")

st.title("🤖 Asistente IA para Empresas")
st.caption("Tu plataforma completa de inteligencia artificial para empresas")

st.sidebar.title("🧩 Módulos")
modulo = st.sidebar.radio("Elige un módulo:", [
    "📄 Procesar documentos",
    "✍️ Generar documentos",
])

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
                with st.spinner("Procesando..."):
                    resultado = procesar_documento(texto, instruccion)
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
                    st.download_button("📥 Descargar Excel", data=buffer,
                        file_name="resultado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except:
                    st.info("💡 El resultado no es JSON puro, no se puede exportar a Excel.")

        elif modo == "💬 Hacer preguntas al documento":
            pregunta = st.text_input("Tu pregunta:", placeholder="¿Cuál es el importe total?")
            if st.button("💬 Preguntar") and pregunta:
                with st.spinner("Pensando..."):
                    respuesta = procesar_pregunta(texto, pregunta)
                st.write(respuesta)

        elif modo == "📝 Resumir documento":
            if st.button("📝 Generar resumen"):
                with st.spinner("Resumiendo..."):
                    resumen = procesar_pregunta(texto, "Haz un resumen ejecutivo claro y estructurado.")
                st.write(resumen)

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
                with st.spinner("Generando contrato con IA..."):
                    resultado = generar_contrato({
                        "tipo": tipo, "proveedor": proveedor, "cliente": cliente,
                        "servicio": servicio, "importe": importe,
                        "duracion": duracion, "fecha_inicio": fecha_inicio
                    })
                st.subheader("📋 Contrato generado:")
                st.text_area("", resultado, height=500)
                st.download_button("📥 Descargar contrato (.txt)", resultado,
                    file_name="contrato.txt", mime="text/plain")
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
        servicios = st.text_area("Servicios/Productos y precios:",
            placeholder="Desarrollo web: 2000€\nMantenimiento mensual: 200€\nFormación: 500€")

        if st.button("💰 Generar presupuesto"):
            if empresa and cliente and servicios:
                with st.spinner("Generando presupuesto con IA..."):
                    resultado = generar_presupuesto({
                        "empresa": empresa, "cliente": cliente,
                        "servicios": servicios, "validez": validez, "fecha": fecha
                    })
                st.subheader("💰 Presupuesto generado:")
                st.text_area("", resultado, height=500)
                st.download_button("📥 Descargar presupuesto (.txt)", resultado,
                    file_name="presupuesto.txt", mime="text/plain")
            else:
                st.warning("Rellena empresa, cliente y servicios.")

    elif tipo_doc == "📊 Informe ejecutivo":
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa:")
            tema = st.text_input("Tema del informe:", placeholder="Ventas Q1 2026")
        with col2:
            periodo = st.text_input("Período:", placeholder="Enero - Marzo 2026")
        datos = st.text_area("Datos clave:",
            placeholder="Ventas totales: 150.000€\nClientes nuevos: 23\nTicket medio: 6.500€")

        if st.button("📊 Generar informe"):
            if empresa and tema and datos:
                with st.spinner("Generando informe con IA..."):
                    resultado = generar_informe({
                        "empresa": empresa, "tema": tema,
                        "periodo": periodo, "datos": datos
                    })
                st.subheader("📊 Informe generado:")
                st.text_area("", resultado, height=500)
                st.download_button("📥 Descargar informe (.txt)", resultado,
                    file_name="informe.txt", mime="text/plain")
            else:
                st.warning("Rellena empresa, tema y datos.")