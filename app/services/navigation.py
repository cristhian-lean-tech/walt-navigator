import json
from typing import Dict, List, Optional, Any
from numpy import dot
from numpy.linalg import norm

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os

from app.shared.const import CollectionName
from .embdding import EmbeddingService
from .text_normalizer import TextNormalizer
from .conversation_manager import ConversationManager
from app.shared.paths import PATHS
from app.shared.forms import FORMS

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.environ.get("OPENAI_API_KEY"))

prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
Clasifica la siguiente solicitud en una de las siguientes categorías:
- BENEFICIO: si el usuario desea pedir vacaciones, días libres, gimnasio, etc.
- EMPRESA: si el usuario pregunta sobre la empresa, jefe, políticas, etc.
- OTRO: si no pertenece a ninguna de las anteriores.

Mensaje: "{user_input}"
Respuesta (solo la categoría):
"""
)

intent_classifier = LLMChain(llm=llm, prompt=prompt)

sessions = {}
user_states: Dict[str, Dict[str, Any]] = {}
benefit_sessions: Dict[str, Dict[str, Any]] = {}

class NavigationService():

    def __init__(self):
        self.memory = ConversationBufferMemory()
        self.embedding_service = EmbeddingService()
        self.text_normalizer = TextNormalizer()
        self.conversation_manager = ConversationManager()
        self.benefit_embeddings = {}
        self.benefit_synonyms = self._init_benefit_synonyms()
        self._init_benefit_embeddings()  # Inicializar embeddings al crear la instancia
    
    def detect_user_intent(self, content: str, user_id: str) -> Optional[str]:
        result = intent_classifier.run(content)
        session = self.get_user_session(user_id)
        response = session.run(content)
        return result, response

    def get_user_session(self, user_id: str):
        if user_id not in sessions:
            sessions[user_id] = ConversationChain(
                llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.environ.get("OPENAI_API_KEY")),
                memory=ConversationBufferMemory(return_messages=True),
                verbose=False
            )
        return sessions[user_id]
    
    def process_user_input(self, user_id: str, content: str) -> str:
        intent, chat_response = self.detect_user_intent(content, user_id)
        current_state = user_states.get(user_id)

        if current_state and current_state["intent"] != intent:
            # El usuario cambió de intención (empresa ➝ beneficio o viceversa)
            user_states[user_id] = {"intent": intent}
        
        if intent == "BENEFICIO":
            return self.handle_benefit_flow(user_id, content)
        
        elif intent == "EMPRESA":
            return chat_response  # ya viene con contexto
        
        else:
            return "Lo siento, no puedo ayudarte con eso todavía 😅."

    def _get_benefit_config(self, content: str):
        content = content.lower()
        for item in PATHS:
            if item["description"].lower() in content or any(p in content for p in item["description"].lower().split()):
                return item
        return None

    def handle_benefit_flow(self, user_id: str, content: str) -> str:
        session = self.benefit_sessions.get(user_id)

        if not session:
            benefit_config = self._get_benefit_config(content)
            if not benefit_config:
                return "¿Qué beneficio deseas solicitar? Por ejemplo: vacaciones, gimnasio, educación..."

            self.benefit_sessions[user_id] = {
                "benefit": benefit_config["description"],
                "path": benefit_config["path"],
                "fields": {},
                "parametros": benefit_config.get("parametros", [])
            }

            if not benefit_config.get("parametros"):
                del self.benefit_sessions[user_id]
                return f"✅ Puedes acceder directamente a tu solicitud aquí: {benefit_config['path']}"

            first_param = benefit_config["parametros"][0]
            return f"Perfecto, estás solicitando **{benefit_config['description']}**. ¿Cuál es {first_param['text']}?"

        # Continuar flujo
        parametros = session["parametros"]
        for param in parametros:
            if param["id"] not in session["fields"]:
                session["fields"][param["id"]] = content
                break

        # Verificar si falta alguno
        faltantes = [p for p in parametros if p["id"] not in session["fields"]]
        if faltantes:
            siguiente = faltantes[0]
            return f"¿Cuál es {siguiente['text']}?"

        # Completo
        summary = "\n".join([f"- **{k}**: {v}" for k, v in session["fields"].items()])
        path = session["path"]
        del self.benefit_sessions[user_id]

        return f"✅ Aquí está tu solicitud para **{session['benefit']}**:\n{summary}\n\nPuedes enviarla desde: {path}"

    def suggest_routes(self, content: str, role: str, conversation_id: str) -> Dict[str, Any]:
        # Normalizar el texto de entrada
        normalized_content = self.text_normalizer.normalize(content)
        
        # Obtener el estado actual de la conversación
        conversation_state = self.conversation_manager.get_or_create_conversation(conversation_id)
        
        # Si ya tenemos un beneficio, procesar el parámetro actual
        if conversation_state.benefit:
            return self._process_parameter_response(conversation_id, normalized_content)
        
        # Si no tenemos un beneficio, detectarlo
        keywords = self.text_normalizer.get_keywords(normalized_content)
        detected_benefit = self._detect_benefit_combined(normalized_content, keywords)
        
        if detected_benefit:
            # Inicializar la conversación con el beneficio detectado
            self.conversation_manager.update_conversation(
                conversation_id, 
                benefit=detected_benefit
            )
            
            # Obtener el primer parámetro requerido
            next_parameter = self.conversation_manager.get_next_parameter(conversation_id)
            if next_parameter:
                question = FORMS[detected_benefit][next_parameter]
                return {
                    "message": f"Great! You're requesting {detected_benefit}. {question}",
                    "conversation_id": conversation_id,
                    "current_parameter": next_parameter,
                    "benefit": detected_benefit
                }
        
        # Si no se detectó un beneficio, buscar en la base de datos vectorial
        result = self.embedding_service.search_text(normalized_content, CollectionName.NAVIGATION)
        return self._parse_response(result)
    
    def _parse_response(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output = []
        for id_value, metadata, distance in zip(results["ids"][0], results["metadatas"][0], results["distances"][0]):
            output.append({
                  "path": id_value,
                  "description": metadata["short_description"],
                  "score": round((1-distance), 2)
            })
         
        return [output for output in output]

    def _process_parameter_response(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """
        Procesa la respuesta del usuario para el parámetro actual.
        """
        state = self.conversation_manager.get_or_create_conversation(conversation_id)
        current_parameter = state.current_parameter or self.conversation_manager.get_next_parameter(conversation_id)
        
        if not current_parameter:
            return {
                "message": "I'm not sure what information you're providing. Could you please clarify?",
                "conversation_id": conversation_id,
                "benefit": state.benefit
            }
        
        # Actualizar el parámetro con la respuesta del usuario
        self.conversation_manager.update_conversation(
            conversation_id,
            parameter=current_parameter,
            value=content
        )
        
        # Verificar si la conversación está completa
        if self.conversation_manager.is_conversation_complete(conversation_id):
            summary = self.conversation_manager.get_conversation_summary(conversation_id)
            return {
                "message": f"Perfect! I have all the information needed for your {summary['benefit']} request:\n" + 
                          "\n".join([f"- {param}: {value}" for param, value in summary['parameters'].items()]) +
                          "\nWould you like to submit this request?",
                "conversation_id": conversation_id,
                "summary": summary,
                "benefit": summary['benefit'],
                "is_complete": True
            }
        
        # Obtener el siguiente parámetro
        next_parameter = self.conversation_manager.get_next_parameter(conversation_id)
        if next_parameter:
            question = FORMS[state.benefit][next_parameter]
            return {
                "message": question,
                "conversation_id": conversation_id,
                "current_parameter": next_parameter,
                "benefit": state.benefit
            }
        
        return {
            "message": "I'm not sure what to ask next. Could you please clarify?",
            "conversation_id": conversation_id,
            "benefit": state.benefit
        }

    def _init_benefit_synonyms(self) -> Dict[str, List[str]]:
        """
        Inicializa un diccionario de sinónimos para cada beneficio.
        """
        synonyms = {}
        for benefit in FORMS.keys():
            # Agregar el beneficio original
            synonyms[benefit] = [benefit]
            
            # Agregar sinónimos usando el normalizador
            normalized_benefit = self.text_normalizer.normalize(benefit)
            benefit_synonyms = self.text_normalizer.get_synonyms(normalized_benefit)
            synonyms[benefit].extend(benefit_synonyms)
            
            # Agregar variaciones comunes
            if "vacation" in benefit:
                synonyms[benefit].extend(["holiday", "time off", "leave"])
            elif "gym" in benefit:
                synonyms[benefit].extend(["fitness", "workout", "exercise"])
            elif "days off" in benefit:
                synonyms[benefit].extend(["day off", "personal day", "time off"])
        
        return synonyms

    def _detect_benefit_combined(self, content: str, keywords: List[str]) -> Optional[str]:
        """
        Combina múltiples métodos para detectar beneficios de manera más robusta.
        """
        # 1. Detección por palabras clave (más confiable para español)
        for benefit, synonyms in self.benefit_synonyms.items():
            # Verificar si alguna palabra clave coincide con los sinónimos
            if any(keyword in synonyms for keyword in keywords):
                return benefit

        # 2. Detección por similitud semántica (si hay embeddings disponibles)
        if self.benefit_embeddings:
            semantic_match = self._semantic_detect_benefit(content)
            if semantic_match:
                return semantic_match

        # 3. Detección por coincidencia exacta
        for benefit in FORMS.keys():
            if benefit in content:
                return benefit

        return None

    def _semantic_detect_benefit(self, content: str) -> Optional[str]:
        """
        Detecta beneficios usando similitud semántica con embeddings.
        """
        if not self.benefit_embeddings:
            return None

        query_embedding = self.embedding_service.generate_embedding(content)

        def cosine_similarity(a, b):
            return dot(a, b) / (norm(a) * norm(b))

        scores = {
            benefit: cosine_similarity(query_embedding, emb)
            for benefit, emb in self.benefit_embeddings.items()
        }

        if not scores:
            return None

        best_match, best_score = max(scores.items(), key=lambda x: x[1])
        return best_match if best_score > 0.65 else None

    def _detect_benefit(self, content: str) -> str or None:
        for benefit in FORMS.keys():
           if benefit in content.lower():
               return benefit            
        return None

    def _init_benefit_embeddings(self):
        from app.shared.forms import FORMS
        self.benefit_embeddings = {
            benefit: self.embedding_service.generate_embedding(benefit)
            for benefit in FORMS.keys()
        }

#  Fase 1: Mejorar la detección de beneficios
# ✅ Usar embeddings en lugar de palabras clave (_detect_benefit) para detectar intenciones más naturalmente.
# ⬆️ Hacer que reconozca sinónimos, errores ortográficos o frases largas.
# 💬 Fase 2: Flujos conversacionales dinámicos
# ✅ Cada beneficio puede tener parámetros (como fechas, tipo de solicitud, etc).
# 🔁 Hacer preguntas personalizadas según el beneficio detectado.
# 💾 Guardar respuestas en sesión temporal (en memoria por ahora).
# 📝 Fase 3: Registro de solicitudes
# 🗃 Guardar cada solicitud en base de datos o archivo (quién pidió qué y cuándo).
# 🕵️‍♀️ Auditar peticiones o generar reportes.
# 🤖 Fase 4: Integraciones externas
# 💬 Integrar con Slack, WhatsApp o frontend Web con botones.
# 🔔 Notificaciones automáticas o correos.
# 📦 Fase 5: Despliegue y monitoreo
# 🐳 Docker funcional.
# 🚦 Health checks y logs.
# 📊 Métricas básicas del sistema.