import json
from typing import Dict, Optional, Any, List
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

MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

llm = ChatOpenAI(temperature=0, model=MODEL_NAME, openai_api_key=os.environ.get("OPENAI_API_KEY"))

prefix = "Clasifica la siguiente solicitud en una de las categorías: BENEFICIO, EMPRESA, USUARIO, SOPORTE, OTRO.\n\n"
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
- SOPORTE: si el usuario tiene problemas técnicos, necesita soporte IT, problemas con equipos, software, licencias, etc.
- USUARIO: si el usuario pregunta sobre información personal suya.
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
    
    def detect_request_type(self, content: str, user_id: str) -> Optional[str]:
        request_type = request_type_chain.invoke({"user_input":content})

        return request_type["text"]
    
    def process_user_input(self, content: str, user_type: str, user_id: str) -> Dict[str, Any]:
        request_type = self.detect_request_type(content, user_id)        

        benefit_route = self.embedding_service.search_text(
            text=content,
            collection_name=CollectionName.NAVIGATION,
            where={"$or": [{"user_type": user_type}, {"user_type": "any"}]}
        )

        
        benefit_route = self._parse_response(benefit_route)
        
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
    
    def _parse_response(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output = []
        for id_value, metadata, distance in zip(results["ids"][0], results["metadatas"][0], results["distances"][0]):
            output.append({
                  "path": id_value,
                  "description": metadata["short_description"],
                  "score": round((1-distance), 2)
            })
         
        return output

    def clean_up_database(self):
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        collection.delete()

