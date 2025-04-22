import json
from typing import Dict, Optional, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

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
    
    def detect_request_type(self, content: str, user_id: str) -> Optional[str]:
        request_type = request_type_chain.invoke({"user_input":content})

        return request_type["text"]
    
    def process_user_input(self, content: str, user_type: str, user_id: str) -> Dict[str, Any]:
        request_type = self.detect_request_type(content, user_id)

        benefit_route = self.embedding_service.search_text(
            text=content,
            collection_name=CollectionName.NAVIGATION,
            where={"user_type": user_type}
        )

        print("*** ROUTE: ", benefit_route)
      
        response = benefit_route_chain.invoke({"matches": json.dumps(benefit_route, indent=2)})
        result = json.loads(response["text"])
        response = {
            "response": result.get("message"),
            "paths": benefit_route or None,
            "request_type": request_type
        }

        return response
    
        
        if request_type == "BENEFICIO":
            benefit_route = self.embedding_service.search_text(
                text=content,
                collection_name=CollectionName.NAVIGATION
                )
            
            print(f"**** ROUTE: ", benefit_route)
            
            response = benefit_route_chain.invoke({"matches": json.dumps(benefit_route, indent=2)})
            result = json.loads(response["text"])
            response = {
                "response": result.get("message"),
                "paths": result.get("paths"),
                "request_type": request_type
                }            

            return response
        
        return {
                "response": "Lo siento, no puedo ayudarte con eso todavía 😅.",
                "path": None,
                "request_type": request_type
                }

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

    def init_database(self):
        databseWasInitialized = self.embedding_service.exists_collection(CollectionName.NAVIGATION)
        if databseWasInitialized:
            return
        
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        ids = [item["path"] for item in PATHS]
        documents = [item["description"] for item in PATHS]
        metadatas = [{"user_type": item["user_type"], "short_description": item["short_description"]} for item in PATHS]

        print(f"**** IDs: ", metadatas)

        collection.add(
            ids=ids,
            embeddings=[self.embedding_service.generate_embedding(doc) for doc in documents],
            metadatas=metadatas
        )

    def cleanup_database(self):
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        collection.delete()

    