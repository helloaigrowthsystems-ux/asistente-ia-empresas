from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generar_contrato(datos: dict) -> str:
    prompt = f"""
    Genera un contrato profesional con estos datos:

    Tipo de contrato: {datos.get('tipo')}
    Empresa/Proveedor: {datos.get('proveedor')}
    Cliente: {datos.get('cliente')}
    Servicio: {datos.get('servicio')}
    Importe: {datos.get('importe')}
    Duración: {datos.get('duracion')}
    Fecha de inicio: {datos.get('fecha_inicio')}

    Genera un contrato completo, profesional y legalmente estructurado en español.
    Incluye: encabezado, partes, objeto del contrato, precio, duración, 
    obligaciones, condiciones de rescisión y firmas.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content


def generar_presupuesto(datos: dict) -> str:
    prompt = f"""
    Genera un presupuesto profesional con estos datos:

    Empresa: {datos.get('empresa')}
    Cliente: {datos.get('cliente')}
    Servicios/Productos: {datos.get('servicios')}
    Validez del presupuesto: {datos.get('validez')}
    Fecha: {datos.get('fecha')}

    Genera un presupuesto completo y profesional en español con:
    desglose de servicios, precios, IVA, total y condiciones.
    Formato claro y presentable.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content


def generar_informe(datos: dict) -> str:
    prompt = f"""
    Genera un informe ejecutivo profesional sobre:

    Empresa: {datos.get('empresa')}
    Tema del informe: {datos.get('tema')}
    Período: {datos.get('periodo')}
    Datos clave: {datos.get('datos')}

    Genera un informe ejecutivo completo en español con:
    resumen ejecutivo, análisis, conclusiones y recomendaciones.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content