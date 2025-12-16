from dataclasses import dataclass
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
import os
from typing import Optional

from app.services.prompts import faq_intent_classifier_prompt, faq_small_talk_prompt


@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

@dataclass
class FaqsResponseDTO:
    punny_response: str
    answer: str
    #link: Optional[str] = None
    #point_of_contact: Optional[str] = None


SMALL_TALK_PROMPT = """
Eres un asistente interno de soporte de la empresa.

Alcance: SOLO SMALL TALK (saludos, agradecimientos, despedidas, frases cortas sin solicitud concreta).

Reglas:
- Responde en 1–2 frases, tono amable y profesional.
- No inventes información de la empresa.
- Cierra ofreciendo ayuda en temas de trabajo: beneficios, RRHH/onboarding, time off/PTO, pagos/fee, herramientas internas (WALT/My Board), soporte IT.

Ejemplos:
- "Hola" => "Hola. ¿En qué puedo ayudarte con beneficios, RRHH, time off o soporte IT?"
"""
FAQS_PROMPT = """You are a FAQS agent to answer questions about the company to their employees and create a new IT support request if the employee needs it.
    IMPORTANT INSTRUCTIONS:
    - After calling a tool, you MUST provide a final answer and STOP. Do not call tools repeatedly.
    - Use the tools only ONCE per question.
    You have the following tools:
    - create_it_support_request: to create a new IT support request (use only if user needs IT support)
    """

checkpointer = InMemorySaver()
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
model = init_chat_model(MODEL_NAME, temperature=0.2, timeout=10, max_tokens=1000)

@tool
def create_it_support_request(question: str, context: ToolRuntime[Context]) -> FaqsResponseDTO:
    """Create a new IT support request. Use this tool ONLY ONCE when the user needs IT support."""    
    result = _create_it_support_request_agent.invoke({
        "messages": [HumanMessage(content=question)]
    })
    return result

_small_talk_agent = create_agent(
    model=model,
    system_prompt=SMALL_TALK_PROMPT,
    context_schema=Context,
    checkpointer=checkpointer,
)

_faqs_agent = create_agent(
                model=model,
                system_prompt=FAQS_PROMPT,
                context_schema=Context,
                tools=[create_it_support_request],
                checkpointer=checkpointer,
            )

_create_it_support_request_agent = create_agent(
                model=model,
                system_prompt=FAQS_PROMPT,
                context_schema=Context,
                tools=[create_it_support_request],
                checkpointer=checkpointer,
            )

@tool
def small_talk(question: str, context: ToolRuntime[Context]) -> str:
    """Respond to small talk questions."""
    result = _small_talk_agent.invoke([HumanMessage(content=question)])    
    return result.content

class CompanyChatbotService:
    one_shot_model = None    
    
    @classmethod
    def get_faqs_agent(cls):
        """
        Get or create the FAQS agent (singleton pattern).
        This ensures we only create one agent instance and reuse it.
        """
        return _faqs_agent


    @classmethod
    def get_small_talk_agent(cls):
        """
        Get or create the small talk agent (singleton pattern).
        This ensures we only create one agent instance and reuse it.
        """
        return _small_talk_agent

    @classmethod
    def get_one_shot_model(cls):
        """
        Get or create the one-shot intent classifier agent (singleton pattern).
        This uses the faq_intent_classifier_prompt template to classify user input.
        """
        if cls.one_shot_model is None:
            # Create the LLM chain with the few-shot prompt template
            MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
            cls.one_shot_model = init_chat_model(MODEL_NAME, temperature=0.2, timeout=15, max_tokens=150)
        return cls.one_shot_model

    def __init__(self):
        # Configurar el modelo de lenguaje
        MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
        model = init_chat_model(MODEL_NAME, temperature=0.5, timeout=10, max_tokens=1000)
        # Set max_iterations to prevent infinite loops
        self.max_iterations = 5

        # Initialize one-shot agent using the class method
        self.one_shot_model = init_chat_model(MODEL_NAME, temperature=0.2, timeout=10, max_tokens=1000)

#    def _build_prompt(self):
#        # Plantilla de prompt para el agente
#        template = """
#Eres un asistente virtual de la compañía. Responde preguntas sobre la compañía y ayuda a los usuarios a solicitar beneficios.
#Los beneficios disponibles son: vacaciones, time off y otros. Algunos beneficios requieren parámetros adicionales:
#- Vacaciones: requiere fecha de inicio y fecha de fin.
#- Time off: no requiere parámetros adicionales.
#
#Si el usuario solicita un beneficio, verifica si requiere parámetros adicionales y solicítalos si no están presentes.
#Si el beneficio está disponible, proporciona la ruta correspondiente desde la carpeta `shared/paths`.
#
#Conversación previa:
#{history}
#
#Usuario: {input}
#Asistente:
#"""
#        return PromptTemplate(input_variables=["history", "input"], template=template)

    def handle_user_input(self, user_input):
        # Procesar la entrada del usuario
        response = self.conversation_chain.run(input=user_input)
        return response

    def get_benefit_path(self, benefit_name):
        # Obtener la ruta del beneficio
        return self.benefits_paths.get(benefit_name.lower(), "Beneficio no encontrado.")
