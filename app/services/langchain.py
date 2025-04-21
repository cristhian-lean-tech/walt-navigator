from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import os

class CompanyChatbotService:
    def __init__(self):
        # Configurar el modelo de lenguaje
        self.chat_model = ChatOpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory()
        self.conversation_chain = ConversationChain(
            llm=self.chat_model,
            memory=self.memory,
            prompt=self._build_prompt()
        )
        # Rutas de beneficios
        self.benefits_paths = {
            "vacaciones": "shared/paths/vacaciones",
            "time_off": "shared/paths/time_off",
            # Agrega más beneficios según sea necesario
        }

    def _build_prompt(self):
        # Plantilla de prompt para el agente
        template = """
Eres un asistente virtual de la compañía. Responde preguntas sobre la compañía y ayuda a los usuarios a solicitar beneficios.
Los beneficios disponibles son: vacaciones, time off y otros. Algunos beneficios requieren parámetros adicionales:
- Vacaciones: requiere fecha de inicio y fecha de fin.
- Time off: no requiere parámetros adicionales.

Si el usuario solicita un beneficio, verifica si requiere parámetros adicionales y solicítalos si no están presentes.
Si el beneficio está disponible, proporciona la ruta correspondiente desde la carpeta `shared/paths`.

Conversación previa:
{history}

Usuario: {input}
Asistente:
"""
        return PromptTemplate(input_variables=["history", "input"], template=template)

    def handle_user_input(self, user_input):
        # Procesar la entrada del usuario
        response = self.conversation_chain.run(input=user_input)
        return response

    def get_benefit_path(self, benefit_name):
        # Obtener la ruta del beneficio
        return self.benefits_paths.get(benefit_name.lower(), "Beneficio no encontrado.")

# Ejemplo de uso
if __name__ == "__main__":
    chatbot_service = CompanyChatbotService()
    print("Bienvenido al chatbot de la compañía. Escribe 'salir' para terminar la conversación.")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() == "salir":
            print("Asistente: ¡Hasta luego!")
            break

        response = chatbot_service.handle_user_input(user_input)
        print(f"Asistente: {response}")