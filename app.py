import streamlit as st
import os
import json
import re
import pandas as pd
from io import BytesIO
from file_handler import extraer_texto_pdf, extraer_texto_excel
from ai_processor import procesar_documento, procesar_pregunta

st.set_page_config(page_title="IA para Empresas", page_icon="🤖", layout="wide")

st.title("🤖 Asistente IA para Empresas")
st.caption("Procesa facturas, contratos, reportes y cualquier documento automáticamente")

st.sidebar.title("⚙️ Modo de uso")
modo = st.sidebar.radio("¿Qué quieres hacer?", [
    "📊 Extraer datos estructurados",
    "💬 Hacer preguntas al documento",
    "📝 Resumir documento"
])

archivo = st.file_uploader(
    "Sube tu documento",
    type=["pdf", "xlsx", "xls"],
    help="PDF o Excel"
)

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
        st.subheader("¿Qué datos quieres extraer?")

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

            st.subheader("📋 Resultado:")
            st.code(resultado, language="json")

            # Exportar a Excel
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
                    label="📥 Descargar Excel",
                    data=buffer,
                    file_name="resultado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except:
                st.info("💡 Tip: el resultado no es JSON puro, no se puede exportar a Excel.")

    elif modo == "💬 Hacer preguntas al documento":
        st.subheader("Pregúntale cualquier cosa al documento")
        pregunta = st.text_input("Tu pregunta:", placeholder="¿Cuál es el importe total?")

        if st.button("💬 Preguntar") and pregunta:
            with st.spinner("Pensando..."):
                respuesta = procesar_pregunta(texto, pregunta)
            st.subheader("💡 Respuesta:")
            st.write(respuesta)

    elif modo == "📝 Resumir documento":
        if st.button("📝 Generar resumen"):
            with st.spinner("Resumiendo..."):
                resumen = procesar_pregunta(
                    texto,
                    "Haz un resumen ejecutivo claro y estructurado de este documento."
                )
            st.subheader("📋 Resumen:")
            st.write(resumen)

    os.remove(ruta_temp)

else:
    st.info("👆 Sube un documento para empezar")