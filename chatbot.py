from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def chatbot_responder(historial: list, informacion_empresa: str, pregunta: str) -> str:
    system_prompt = f"""
    Eres el asistente virtual de una empresa. Responde SOLO basándote en la 
    información que te proporcionan sobre la empresa. Si no sabes algo, 
    di que no tienes esa información y sugiere contactar directamente.

    INFORMACIÓN DE LA EMPRESA:
    {informacion_empresa}

    Responde siempre en español, de forma profesional y amable.
    """

    mensajes = [{"role": "system", "content": system_prompt}]

    for msg in historial:
        mensajes.append(msg)

    mensajes.append({"role": "user", "content": pregunta})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=mensajes,
        max_tokens=1000
    )
    return response.choices[0].message.content