from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

EXAMPLES_REQUEST_TYPE = [
    # BENEFICIO - Vacaciones y días libres
    {"input": "I want vacations, what can I do?", "output": "BENEFICIO"},
    {"input": "Quiero pedir vacaciones", "output": "BENEFICIO"},
    {"input": "How many days off do I have?", "output": "BENEFICIO"},
    {"input": "Necesito un día libre", "output": "BENEFICIO"},
    
    # BENEFICIO - Beneficios y programas
    {"input": "What can you tell me about the gym benefit?", "output": "BENEFICIO"},
    {"input": "¿Qué beneficios tengo?", "output": "BENEFICIO"},
    {"input": "What are my benefits?", "output": "BENEFICIO"},
    {"input": "Educational Benefit/Brain Power", "output": "BENEFICIO"},
    {"input": "What can you tell me about the Child Bonus?", "output": "BENEFICIO"},
    
    # BENEFICIO - Desarrollo profesional y habilidades
    {"input": "How can I participate in the English Classes?", "output": "BENEFICIO"},
    {"input": "How can I improve my Tech Skills?", "output": "BENEFICIO"},
    {"input": "How can I Improve my Soft Skills?", "output": "BENEFICIO"},
    {"input": "¿Cómo puedo participar en las clases de inglés?", "output": "BENEFICIO"},
    
    # EMPRESA - Procesos administrativos y documentación
    {"input": "How can I create my Deel/Via account?", "output": "EMPRESA"},
    {"input": "I need a labor certificate, how can I get one?", "output": "EMPRESA"},
    {"input": "Necesito un certificado laboral", "output": "EMPRESA"},
    {"input": "How can I get a salary increase?", "output": "EMPRESA"},
    {"input": "¿Cómo puedo obtener un aumento de salario?", "output": "EMPRESA"},
    
    # SOPORTE - Soporte técnico e IT
    {"input": "My PC isn't working/I'm having technical issues", "output": "SOPORTE"},
    {"input": "Mi PC no funciona", "output": "SOPORTE"},
    {"input": "How to Create a General IT Support Request", "output": "SOPORTE"},
    {"input": "Requesting Additional IT Equipment", "output": "SOPORTE"},
    {"input": "Email Account Issues (Password or 2FA Authentication)", "output": "SOPORTE"},
    {"input": "Replacement of Equipment or Accessories Due to Malfunction", "output": "SOPORTE"},
    {"input": "Requesting an Equipment Upgrade or Improvement", "output": "SOPORTE"},
    {"input": "Software, License, or Subscription Requests", "output": "SOPORTE"},
    {"input": "Hardware Issues", "output": "SOPORTE"},
    {"input": "Request for Navigation Permissions (Blocked Websites)", "output": "SOPORTE"},
    {"input": "Tengo problemas técnicos con mi computadora", "output": "SOPORTE"},
    {"input": "Necesito solicitar equipo adicional de IT", "output": "SOPORTE"},
    
    # EMPRESA - Crecimiento y desarrollo en la empresa
    {"input": "How can I Grow in Lean Tech?", "output": "EMPRESA"},
    {"input": "¿Cómo puedo crecer en la empresa?", "output": "EMPRESA"},
    
    # USUARIO - Información personal del usuario
    {"input": "¿Cuántos días de vacaciones tengo?", "output": "USUARIO"},
    {"input": "¿Cómo puedo acceder a mi nómina?", "output": "USUARIO"},
    {"input": "Como me llamo?", "output": "USUARIO"},
    
    # OTRO - Preguntas fuera del alcance
    {"input": "¿Qué días son festivos?", "output": "OTRO"},
    {"input": "¿Cuándo son las vacaciones de verano?", "output": "OTRO"},
    {"input": "¿Qué es la capital de Francia?", "output": "OTRO"},
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

# Prompts para clasificación de intenciones en FAQs
EXAMPLES_FAQ_INTENT = [
    {"input": "¿Cómo puedo solicitar vacaciones?", "output": "IN_SCOPE"},
    {"input": "¿Cuál es la política de trabajo remoto?", "output": "IN_SCOPE"},
    {"input": "¿Cómo accedo a mi nómina?", "output": "IN_SCOPE"},
    {"input": "¿Quién es el punto de contacto para beneficios?", "output": "IN_SCOPE"},
    {"input": "¿Cuántos días de vacaciones tengo?", "output": "IN_SCOPE"},
    {"input": "¿Qué es la capital de Francia?", "output": "OUT_OF_SCOPE"},
    {"input": "¿Cómo se hace una pizza?", "output": "OUT_OF_SCOPE"},
    {"input": "¿Cuál es el mejor restaurante de la ciudad?", "output": "OUT_OF_SCOPE"},
    {"input": "Hola", "output": "SMALL_TALK"},
    {"input": "Gracias", "output": "SMALL_TALK"},
    {"input": "Buenos días", "output": "SMALL_TALK"},
    {"input": "¿Cómo estás?", "output": "SMALL_TALK"},
]

faq_intent_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Entrada: {input}\nClasificación: {output}"
)

faq_intent_classifier_prompt = PromptTemplate(
  input_variables=["user_message", "format_instructions"],
  template_format="jinja2",
  template="""You are an intent router for a Lean Tech/WALT internal chatbot. Classify into exactly ONE:

IN_SCOPE: Lean Tech internal FAQs/processes/tools: WALT/My Board, Slack contacts, Airtable forms, Sophos; HR/People (labor certificate, documents), onboarding (Deel/Via), time off/PTO/vacations/service interruption/rest days, fee/salary increase; Growth (ETP/English classes, tech roadmap/technical plan, soft skills, career path); Benefits (Brain Power, Hustle 4 the muscle/Smart Fit code, child/parenthood bonus, referral, monthly lunch, GLIM); IT support (PC/peripherals, hardware damage, replacement, extra equipment, upgrades, software/license/subscription, blocked websites, email password/2FA/locked).
OUT_OF_SCOPE: personal/general/public-knowledge topics not tied to Lean Tech internal context.
SMALL_TALK: greetings/thanks/farewells/social chat with no request.

Rules (apply in order):
1) If mainly greeting/thanks/farewell and no request → SMALL_TALK.
2) If about any IN_SCOPE area above (even if "Lean Tech/WALT" not mentioned; allow Spanglish/typos) → IN_SCOPE.
3) Otherwise → OUT_OF_SCOPE.
4) If vague but plausibly internal ("I need help", "it doesn't work") → IN_SCOPE + needs_clarification=true.

If needs_clarification=true, ask ONE short question to route (benefits/time off/growth/HR-docs/IT). Else clarifying_question must be null.

Return ONLY STRICT JSON with all fields:
intent ("IN_SCOPE"|"OUT_OF_SCOPE"|"SMALL_TALK"), confidence (0-1), needs_clarification (bool),
clarifying_question (string|null), short_reason (<=120 chars).

{{ format_instructions }}

User message:
{{ user_message }}
"""
)

faq_small_talk_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""You are a company support virtual assistant. Your job is to help users with questions about benefits, policies, human resources, technical support, and other work-related topics.
    If the user talks about other subjects, respond politely with a brief conversation, then steer the discussion back to company-related topics and offer assistance.
    IMPORTANT: Respond in the same language as the user (english or spanish).
    Mensaje usuario: 
    {user_input}
    """
)

# Prompt para respuestas conversacionales con contexto
faq_conversational_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""Eres un asistente virtual de soporte de la empresa. Tu trabajo es ayudar a los usuarios con preguntas sobre beneficios, políticas, recursos humanos y temas relacionados con el trabajo.

Cuando respondas:
- Sé amable y profesional
- Usa el contexto de la conversación anterior para dar respuestas más precisas
- Si la pregunta es un seguimiento de algo mencionado antes, haz referencia al contexto
- Mantén respuestas concisas pero útiles
- Si no estás seguro, puedes pedir aclaraciones

Responde en el mismo idioma que el usuario.

Historial de conversación:
{history}

Usuario: {input}
Asistente:"""
)

# Prompt para respuestas cuando no se encuentra información relevante
faq_followup_prompt = PromptTemplate(
    input_variables=["question", "chat_history"],
    template="""Eres un asistente virtual de soporte. El usuario hizo la siguiente pregunta: "{question}"

Historial de conversación:
{chat_history}

No se encontró información específica en la base de conocimientos para esta pregunta. 
Genera una respuesta conversacional y útil que:
1. Reconozca la pregunta del usuario
2. Use el contexto de la conversación anterior si es relevante
3. Sugiera que el usuario reformule la pregunta o proporcione más detalles
4. Sea amable y profesional

Responde en el mismo idioma que el usuario usó en su pregunta.
"""
)

# Prompt para clarificación de preguntas ambiguas
faq_clarification_prompt = PromptTemplate(
    input_variables=["user_question", "retrieved_faqs", "format_instructions"],
    template_format="jinja2",
    template="""You are a company support assistant helping to clarify ambiguous user questions.

The user asked: "{{ user_question }}"

We retrieved the following FAQs from our knowledge base:
{{ retrieved_faqs }}

Your task:
1. Analyze if ANY of the retrieved FAQs are related to the user's question
2. If they ARE related but ambiguous (multiple options), generate a clarifying question to help identify which specific FAQ the user needs
3. If they are NOT related, generate a clarifying question to better understand what the user is asking about

Guidelines:
- The clarifying question should be concise (1-2 sentences max)
- It should help distinguish between the options if multiple FAQs are relevant
- It should ask for specific details if the question is too vague
- Respond in the same language as the user's question 
- Be friendly and professional

{{ format_instructions }}

Return a JSON object with:
- is_related: boolean (true if at least one FAQ is related to the question)
- clarifying_question: string (the question to ask the user, or null if not needed)
- related_faq_indexes: array of numbers (indexes of FAQs that are related, empty if none)
"""
)

# Prompt for handling clarification responses
faq_clarification_response_prompt = PromptTemplate(
    input_variables=["original_question", "user_response", "available_faqs", "format_instructions"],
    template_format="jinja2",
    template="""You are a company support assistant analyzing a user's response to a clarification question.

Original question: "{{ original_question }}"
User's response: "{{ user_response }}"

Available FAQs:
{{ available_faqs }}

Your task:
1. Analyze if the user's response helps identify which FAQ they need
2. Determine which FAQ (if any) best matches based on their clarification
3. If the response is too vague or doesn't match any FAQ, indicate that more clarification is needed

Guidelines:
- Look for keywords, confirmations (yes/no), or specific details in the user's response
- Match the response to the most relevant FAQ
- If the user says "yes", "correct", "that one", etc., choose the first/most relevant FAQ
- If the user says "no", "neither", "none", etc., indicate no match
- If unclear, request more clarification
- Be context-aware: the user might be answering the clarification question directly

{{ format_instructions }}

Return a JSON object with:
- selected_faq_index: number or null (the index of the selected FAQ, null if none match)
- needs_more_clarification: boolean (true if the response is too vague)
- confidence: float between 0.0 and 1.0 (how confident you are in the selection)
"""
)