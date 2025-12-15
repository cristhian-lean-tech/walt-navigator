import os
import asyncio
from typing import Dict, Optional, Literal
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langdetect import detect
from app.dtos.faqs import IntentClassifierOutput
from app.services.langchain import CompanyChatbotService
from app.services.embdding import EmbeddingService
from app.services.prompts import faq_intent_classifier_prompt, faq_small_talk_prompt
from app.services.embdding import CollectionName
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from app.dtos.faqs import FaqsResponseDTO
from app.services.faqs_mapper import from_string_to_faqs_response_dto, from_dict_to_faqs_response_dto


MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

RAG_STATE = Literal["NO_RESULTS", "LOW_ACCURACY", "HIGH_ACCURACY"]
RAG_ACTION = Literal["ANSWER", "REQUEST_CLARIFICATION", "NO_RESULTS"]
class RAGState(BaseModel):
    index: int
    distance: float
    state: RAG_STATE
class GetRAGStateOutput(BaseModel):
    action: RAG_ACTION
    states: list[RAGState]
    indexes: list[int]


class FaqsService2:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def get_out_of_scope_message(self, language: str):
        """Return message for out-of-scope questions."""
        messages = {
            'es': "Lo siento, pero solo puedo ayudarte con preguntas relacionadas con soporte, beneficios, políticas de la empresa y temas relacionados con el trabajo. ¿Hay algo específico sobre estos temas en lo que pueda ayudarte?",
            'en': "I'm sorry, but I can only help you with questions related to support, benefits, company policies, and work-related topics. Is there something specific about these topics I can help you with?"
        }
        return {
            "answer": messages.get(language, messages['en']),
            "link": "",
            "point_of_contact": ""
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect if the text is in Spanish or English."""
        try:
            detected_lang = detect(text)
            return 'es' if detected_lang == 'es' else 'en'
        except:
            return 'en'

    def ask_faqs_agent(self, question: str, contract_type: str, user_id: str) -> FaqsResponseDTO:
        intent = self.get_intent(question)
        language = self._detect_language(question)

        match (intent):
            case "SMALL_TALK":
                return from_string_to_faqs_response_dto(self.start_small_talk(question), question)
            case "IN_SCOPE":
                result = self.in_scope_conversation(question, language, contract_type, user_id)
                return from_dict_to_faqs_response_dto(result)
            case "OUT_OF_SCOPE":
                result = self.get_out_of_scope_message(language)
                return from_dict_to_faqs_response_dto(result)
            case _:
                result = self.get_out_of_scope_message(language)
                return from_dict_to_faqs_response_dto(result)

    def get_intent(self, question: str):
        parser = PydanticOutputParser(pydantic_object=IntentClassifierOutput)        
        chain = faq_intent_classifier_prompt | CompanyChatbotService.get_one_shot_model() | parser
        category_response: IntentClassifierOutput = chain.invoke({
            "user_message": question,
            "format_instructions": parser.get_format_instructions()
        })
        intent = category_response.intent
        print(f"[INTENT] {intent}")
        return intent

    def start_small_talk(self, question: str) -> str:
        small_talk_chain = faq_small_talk_prompt | CompanyChatbotService.get_one_shot_model()
        small_talk_response = small_talk_chain.invoke({
            "user_input": question
        })

        content = small_talk_response.content
        
        return content

    def in_scope_conversation(self, question: str, language: str, contract_type: str, user_id: str):
        element_number = 2
        faqs = self.embedding_service.search_text(
            text=question,
            collection_name=CollectionName.FAQS,
            n_results=element_number,
            where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]}
        )

        if faqs["ids"][0] and len(faqs["ids"][0]) > 0:
            print(f"[IF]", faqs)
            distances = faqs.get("distances", None)
            print(f"[DISTANCES] {distances}")
            rag_state = self.parse_rag_response(distances[0]) if distances else None
            if not rag_state:
                return self.get_out_of_scope_message(language)

            has_high_accuracy_result = self.has_high_accuracy_result(rag_state.states)
            if has_high_accuracy_result:
                metadata = faqs.get("metadatas", None)[0][rag_state.indexes[0]]
                return {
                    "answer": metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"],
                    "link": metadata["link"],
                    "point_of_contact": metadata["contractor_point_of_contact"] if contract_type == "contractor" else metadata["direct_point_of_contact"]
                }
            
            require_clarification = self.require_clarification(rag_state.states)
            if require_clarification:
                return {
                    "answer": "Necesito más información para responder tu pregunta. ¿Puedes proporcionar más detalles?",
                    "link": "",
                    "point_of_contact": ""
                }

            return self.get_out_of_scope_message(language)

        else:
            return self.get_out_of_scope_message(language)

    def parse_rag_response(self, distances: list[float]) -> GetRAGStateOutput:
        states: list[RAGState] = []
        for distance, index in zip(distances, range(len(distances))):
            state = RAGState(index=index, distance=distance, state="NO_RESULTS")
            state.index = index
            state.distance = distance
            if distance <= 0.4:
                state.state = "HIGH_ACCURACY"
            elif distance > 0.4 and distance <= 0.55:
                state.state = "LOW_ACCURACY"
            else:
                state.state = "NO_RESULTS"

            states.append(state)

        has_high_accuracy = (state.state == "HIGH_ACCURACY" for state in states)
        if has_high_accuracy:
            indexes = [state.index for state in states if state.state == "HIGH_ACCURACY"]
            return GetRAGStateOutput(action="ANSWER", states=states, indexes=indexes)

        has_low_accuracy = (state.state == "LOW_ACCURACY" for state in states)
        if has_low_accuracy:
            indexes = [state.index for state in states if state.state == "LOW_ACCURACY"]
            return GetRAGStateOutput(action="REQUEST_CLARIFICATION", states=states, indexes=indexes)
        
        return GetRAGStateOutput(action="NO_RESULTS", states=states, indexes=[])
        
    def require_clarification(self, states: list[RAGState]) -> bool:
        """
        Determine if clarification is required based on RAG states.
        
        Rules:
        - If one state is LOW_ACCURACY and another is NO_RESULTS, return True
        - If more than one state are LOW_ACCURACY, return True
        - If more than 1 state is HIGH_ACCURACY, return True
        """
        low_accuracy_count = sum(1 for state in states if state.state == "LOW_ACCURACY")
        no_results_count = sum(1 for state in states if state.state == "NO_RESULTS")
        high_accuracy_count = sum(1 for state in states if state.state == "HIGH_ACCURACY")
        
        # Rule 1: If one state is LOW_ACCURACY and another is NO_RESULTS, return True
        if low_accuracy_count >= 1 and no_results_count >= 1:
            return True
        
        # Rule 2: If more than one state are LOW_ACCURACY, return True
        if low_accuracy_count > 1:
            return True
        
        # Rule 3: If more than 1 state is HIGH_ACCURACY, return True
        if high_accuracy_count > 1:
            return True
        
        return False

    def has_high_accuracy_result(self, states: list[RAGState]) -> bool:
        high_accuracy_count = sum(1 for state in states if state.state == "HIGH_ACCURACY")
        return high_accuracy_count == 1


        
