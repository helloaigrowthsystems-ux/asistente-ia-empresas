from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def procesar_documento(texto: str, instruccion: str) -> str:
    prompt = f"""
    Instrucción: {instruccion}

    Documento:
    {texto}

    Responde SOLO en formato JSON limpio, sin explicaciones, sin markdown.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def procesar_pregunta(texto: str, pregunta: str) -> str:
    prompt = f"""
    Basándote en este documento, responde la siguiente pregunta:
    Pregunta: {pregunta}

    Documento:
    {texto}

    Respuesta clara y concisa.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content
