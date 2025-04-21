from langchain.prompts import PromptTemplate, ChatPromptTemplate

EXAMPLES_REQUEST_TYPE = [
    {"input": "Quiero pedir vacaciones", "output": "BENEFICIO"},
    {"input": "¿Quién es el CEO?", "output": "EMPRESA"},
    {"input": "¿Cuántos días tengo de vacaciones?", "output": "USUARIO"},
    {"input": "¿Qué días son festivos?", "output": "OTRO"},
    {"input": "¿Cuál es la política de trabajo remoto?", "output": "EMPRESA"},
    {"input": "¿Cómo puedo acceder a mi nómina?", "output": "USUARIO"},
    {"input": "Necesito un día libre", "output": "BENEFICIO"},
    {"input": "¿Dónde está la oficina?", "output": "EMPRESA"},
    {"input": "¿Cuándo son las vacaciones de verano?", "output": "OTRO"},
    {"input": "¿Qué beneficios ofrece la empresa?", "output": "EMPRESA"},
    {"input": "Como me llamo?", "output": "USUARIO"},
]

request_type_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Entrada: {input}\nClasificación: {output}"
)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Esto es lo que has dicho:\n{chat_history}"),
    ("human", "{user_input}"),
])

benefit_route_prompt = PromptTemplate(
    input_variables=["matches"],
    template="""
Eres un asistente útil que transforma sugerencias técnicas en respuestas naturales para humanos.
A continuación tienes una lista de coincidencias similares extraídas desde una base de datos semántica. Cada ítem contiene una descripción, una ruta y una puntuación de similitud.

Tu tarea es:
1. Elegir los mejores beneficios con un score mayor a 0.5 entre los que aparecen.
2. Devolver un mensaje natural para el usuario explicando qué puede hacer.
3. Incluir las mejores rutas correspondientes en el formato JSON solicitado.

Ejemplo de salida:
{{
  "message": "Parece que estás buscando beneficios. Puedes hacerlo aquí.",
  "paths": ["/services?request=VACATION", "/services?request=HOLIDAY"]
}}

Coincidencias:
{matches}
"""
)