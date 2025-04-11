import json
from typing import Dict, List, Optional, Any
from numpy import dot
from numpy.linalg import norm

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.runnables.history import RunnableWithMessageHistory

import os

from app.shared.const import CollectionName
from .embdding import EmbeddingService
from .text_normalizer import TextNormalizer
from .conversation_manager import ConversationManager
from app.shared.paths import PATHS
from app.shared.forms import FORMS
from .prompts import request_type_prompt, benefit_route_prompt, EXAMPLES_REQUEST_TYPE

MODEL_NAME = os.environ.get("MODEL_NAME")

llm = ChatOpenAI(temperature=0, model=MODEL_NAME, openai_api_key=os.environ.get("OPENAI_API_KEY"))

prefix = "Clasifica la siguiente solicitud en una de las categorías: BENEFICIO, EMPRESA, USUARIO, OTRO.\n\n"
suffix = "\nEntrada: {user_input}\nClasificación:"

few_shot_request_type_template = FewShotPromptTemplate(
    examples=EXAMPLES_REQUEST_TYPE,
    example_prompt=request_type_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["user_input"],
)

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

request_type_chain = LLMChain(llm=llm, prompt=few_shot_request_type_template)
benefit_route_chain = LLMChain(
    llm=llm,
    prompt=benefit_route_prompt
)

sessions = {}
user_states: Dict[str, Dict[str, Any]] = {}
benefit_sessions: Dict[str, Dict[str, Any]] = {}

store: Dict[str, ConversationBufferMemory] = {}

class ConversationService():

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.conversation_manager = ConversationManager()
        self.benefit_sessions = benefit_sessions
        self.init_database()

    def get_user_history(self, conversation_id: str):
        if conversation_id not in store:
            store[conversation_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key="user_input",
            )

        return store[conversation_id]
    
    def detect_request_type(self, content: str, user_id: str) -> Optional[str]:
        request_type = request_type_chain.invoke({"user_input":content})

        return request_type["text"]
        session = self.get_user_session(user_id)
        response = session.invoke(content)

        print(f"**** RESPONSE: ", response["response"])
        return request_type["text"], response["response"]

    def get_user_session(self, user_id: str):
        if user_id not in sessions:
            sessions[user_id] = ConversationChain(
                llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.environ.get("OPENAI_API_KEY")),
                memory=ConversationBufferMemory(return_messages=True),
                verbose=False
            )
        return sessions[user_id]
    
    def process_user_input(self, user_id: str, content: str) -> str:
        request_type = self.detect_request_type(content, user_id)
        
        if request_type == "BENEFICIO":
            benefit_route = self.embedding_service.search_text(
                text=content,
                collection_name=CollectionName.NAVIGATION
                )
            
            print(f"**** BENEFIT ROUTE: ", benefit_route)
            
            response = benefit_route_chain.invoke({"matches": json.dumps(benefit_route, indent=2)})
            result = json.loads(response["text"])
            response = {
                "response": result.get("message"),
                "path": result.get("path"),
                "request_type": request_type
                }            

            return response
        
        elif request_type == "EMPRESA":
            return {
                "response": "Lo siento, no puedo ayudarte con eso todavía 😅.",
                request_type: request_type
            }
            

        return {
                "response": "Lo siento, no puedo ayudarte con eso todavía 😅.",
                request_type: request_type
            }
    
        current_state = user_states.get(user_id)

        if current_state and current_state["intent"] != request_type:
            # El usuario cambió de intención (empresa ➝ beneficio o viceversa)
            user_states[user_id] = {"intent": request_type}
        
        if request_type == "BENEFICIO":
            return self.handle_benefit_flow(user_id, content)
        
        elif request_type == "EMPRESA":
            return chat_response  # ya viene con contexto
        
        else:
            return "Lo siento, no puedo ayudarte con eso todavía 😅."

    def _get_benefit_config(self, content: str):
        matches = self.embedding_service.search_text(
            text=content,
            collection_name=CollectionName.NAVIGATION
        )

        if not matches:
            return None

        best = matches[0][0]  # Primer resultado con mejor score
        print(f"Mejor coincidencia: {best}")
        if best["score"] < 0.75:
            return None  # umbral ajustable

        # Buscar objeto completo en PATHS
        for item in PATHS:
            if item["path"] == best["path"]:
                return item

        return None

    def handle_benefit_flow(self, user_id: str, content: str) -> str:
        session = self.benefit_sessions.get(user_id)

        print(f"**** SESSION: ", session)

        if not session:
            benefit_config = self._get_benefit_config(content)
            print(f"**** BENEFIT CONFIG: ", benefit_config)
            if not benefit_config:
                return "¿Qué beneficio deseas solicitar? Por ejemplo: vacaciones, gimnasio, educación..."

            self.benefit_sessions[user_id] = {
                "benefit": benefit_config["description"],
                "path": benefit_config["path"],
                "fields": {},
                "parametros": benefit_config.get("parametros", [])
            }

            print(f"**** BENEFIT SESSION: ", self.benefit_sessions[user_id])

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

    def init_database(self):
        databseWasInitialized = self.embedding_service.exists_collection(CollectionName.NAVIGATION)
        if databseWasInitialized:
            return
        
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        ids = [item["path"] for item in PATHS]
        documents = [item["description"] for item in PATHS]
        metadatas = [{"description": item["description"]} for item in PATHS]

        collection.add(
            ids=ids,
            embeddings=[self.embedding_service.generate_embedding(doc) for doc in documents],
            metadatas=metadatas
        )

    

    