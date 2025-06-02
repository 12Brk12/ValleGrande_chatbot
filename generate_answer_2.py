from groq import Groq

def generate_answer_streaming(user_question, selected_docs, api_key, on_token_callback=print):
    # Incluir contexto textual
    context = "\n".join([f"{doc['id']}: {doc['text']}" for doc in selected_docs])
    # Incluir links explícitamente
    links = "\n".join([
        f"{doc['id']}: {doc.get('reference_url', '')}" for doc in selected_docs if doc.get('reference_url')
    ])

    SYSTEM_MESSAGE = """
Eres un asistente útil que responde preguntas como un asistente virtual.
Debes utilizar el conjunto de datos proporcionado para responder las preguntas.
No debes proporcionar ninguna información que no esté en las fuentes proporcionadas.
Ambos pdfs tienen información distinta, así que no mezcles información.
Las fuentes están en el siguiente formato: <id>: <texto>.
Por favor, responde siempre en español.
No des respuestas extremadamente largas, solo responde lo que te pidan.
Si la pregunta no está clara, solicita que vuelva a pedirla.
Recuerda siempre ser amable y cortés.
Tu nombre es Vallegrancito, cuando te pidan presentarte responde brevemente qué información  
tienes (aún no cites ningún pdf o página).
Si te agradecen (te dicen gracias) o te dan un cumplido, contéstales educadamente; quiere decir que has hecho un buen trabajo y ya no desean más consultas de momento.
Devuelve los links de las referencias, si se repiten solo devuelve uno.
"""

    client = Groq(api_key=api_key)

    try:
        stream = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": f"{user_question}\n\nSources:\n{context}\n\nReference Links:\n{links}"}
            ],
            temperature=0,
            stream=True
        )

        inside_think = False

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if not delta:
                continue

            if "<think>" in delta:
                inside_think = True
                continue
            if "</think>" in delta:
                inside_think = False
                continue

            if not inside_think:
                on_token_callback(delta)

    except Exception as e:
        on_token_callback(f"\n❌ Error: {e}")
