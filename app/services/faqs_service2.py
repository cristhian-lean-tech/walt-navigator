import os
from typing import Optional, Literal, Any
from langdetect import detect
from app.dtos.faqs import IntentClassifierOutput
from app.services.langchain import CompanyChatbotService
from app.services.embdding import EmbeddingService
from app.services.session_manager import session_manager
from app.services.prompts import faq_intent_classifier_prompt, faq_small_talk_prompt, faq_clarification_prompt, faq_clarification_response_prompt
from app.services.embdding import CollectionName
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
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

class ClarificationOutput(BaseModel):
    is_related: bool
    clarifying_question: Optional[str] = None
    related_faq_indexes: list[int] = []

class ClarificationResponseOutput(BaseModel):
    selected_faq_index: Optional[int] = None
    needs_more_clarification: bool
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


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
        language = self._detect_language(question)
        
        # Check if user has a pending clarification
        if session_manager.has_pending_clarification(user_id):
            result = self.handle_clarification_response(question, language, contract_type, user_id)
            return from_dict_to_faqs_response_dto(result)
        
        intent = self.get_intent(question)
        intent_category = intent.intent

        match (intent_category):
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

    def get_intent(self, question: str) -> IntentClassifierOutput:
        parser = PydanticOutputParser(pydantic_object=IntentClassifierOutput)        
        chain = faq_intent_classifier_prompt | CompanyChatbotService.get_one_shot_model() | parser
        category_response: IntentClassifierOutput = chain.invoke({
            "user_message": question,
            "format_instructions": parser.get_format_instructions()
        })
        
        return category_response

    def start_small_talk(self, question: str) -> str:
        small_talk_chain = faq_small_talk_prompt | CompanyChatbotService.get_one_shot_model()
        small_talk_response = small_talk_chain.invoke({
            "user_input": question
        })

        content = small_talk_response.content
        
        # Ensure content is a string
        if isinstance(content, str):
            return content
        elif isinstance(content, list) and len(content) > 0:
            return str(content[0])
        else:
            return str(content)

    def in_scope_conversation(self, question: str, language: str, contract_type: str, user_id: str):
        element_number = 2
        faqs = self.embedding_service.search_text(
            text=question,
            collection_name=CollectionName.FAQS,
            n_results=element_number,
            where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]}
        )

        if faqs["ids"][0] and len(faqs["ids"][0]) > 0:
            distances = faqs.get("distances", None)
            rag_state = self.parse_rag_response(distances[0]) if distances else None
            if not rag_state:
                return self.get_out_of_scope_message(language)

            has_high_accuracy_result = self.has_high_accuracy_result(rag_state.states)
            if has_high_accuracy_result:
                metadatas = faqs.get("metadatas", None)
                if metadatas and metadatas[0] and rag_state.indexes[0] < len(metadatas[0]):
                    metadata = metadatas[0][rag_state.indexes[0]]
                    return {
                        "answer": metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"],
                        "link": metadata["link"],
                        "point_of_contact": metadata["contractor_point_of_contact"] if contract_type == "contractor" else metadata["direct_point_of_contact"]
                    }
                else:
                    return self.get_out_of_scope_message(language)
            
            require_clarification = self.require_clarification(rag_state.states)
            if require_clarification:
                clarifying_question = self.clarify_question(
                    question=question,
                    faqs=faqs,
                    rag_state=rag_state,
                    language=language,
                    contract_type=contract_type
                )
                if clarifying_question:
                    # Store the pending clarification in session
                    metadatas = faqs.get("metadatas", [])
                    pending_faqs = []
                    if metadatas and metadatas[0]:
                        for idx in rag_state.indexes:
                            if idx < len(metadatas[0]):
                                pending_faqs.append(metadatas[0][idx])
                    
                    session_manager.set_pending_clarification(
                        user_id=user_id,
                        question=question,
                        bot_question=clarifying_question,
                        faqs=pending_faqs,
                        rag_indexes=rag_state.indexes,
                        intent="IN_SCOPE"
                    )
                    
                    return {
                        "answer": clarifying_question,
                        "link": "",
                        "point_of_contact": ""
                    }
                else:
                    return {
                        "answer": "Necesito más información para responder tu pregunta. ¿Puedes proporcionar más detalles?" if language == 'es' else "I need more information to answer your question. Can you provide more details?",
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

    def clarify_question(
        self, 
        question: str, 
        faqs: Any, 
        rag_state: GetRAGStateOutput, 
        language: str,
        contract_type: str
    ) -> Optional[str]:
        """
        Generate a clarifying question when multiple FAQs are retrieved or accuracy is low.
        
        Args:
            question: The user's original question
            faqs: Dictionary with search results from chroma (contains ids, distances, metadatas)
            rag_state: RAG state information with indexes of relevant FAQs
            language: Language code ('es' or 'en')
            contract_type: User contract type ('contractor' or 'direct')
        
        Returns:
            A clarifying question string, or None if clarification cannot be generated
        """
        try:
            # Get the relevant FAQs based on rag_state indexes
            relevant_indexes = rag_state.indexes
            if not relevant_indexes:
                return None
            
            metadatas = faqs.get("metadatas", [])
            if not metadatas or not metadatas[0]:
                return None
            
            # Build the retrieved FAQs context for the LLM
            retrieved_faqs_text = []
            for idx in relevant_indexes:
                if idx < len(metadatas[0]):
                    metadata = metadatas[0][idx]
                    faq_question = metadata.get("question", "")
                    # Get the appropriate answer based on contract type
                    answer_key = "contractor_answer" if contract_type == "contractor" else "direct_answer"
                    faq_answer = metadata.get(answer_key, "")
                    
                    retrieved_faqs_text.append(
                        f"FAQ {idx + 1}:\n"
                        f"Question: {faq_question}\n"
                        f"Answer: {faq_answer}\n"
                    )
            
            retrieved_faqs_context = "\n\n".join(retrieved_faqs_text)
            
            # Create parser for the clarification output
            parser = PydanticOutputParser(pydantic_object=ClarificationOutput)
            
            # Create the chain
            chain = faq_clarification_prompt | CompanyChatbotService.get_one_shot_model() | parser
            
            # Invoke the chain
            clarification_response: ClarificationOutput = chain.invoke({
                "user_question": question,
                "retrieved_faqs": retrieved_faqs_context,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Return the clarifying question if available
            return clarification_response.clarifying_question
            
        except Exception as e:
            print(f"[ERROR in clarify_question] {str(e)}")
            # Return a default clarifying question in the appropriate language
            if language == 'es':
                return "Necesito más información para responder tu pregunta. ¿Puedes proporcionar más detalles sobre lo que necesitas?"
            else:
                return "I need more information to answer your question. Can you provide more details about what you need?"
    
    def handle_clarification_response(
        self, 
        user_response: str, 
        language: str, 
        contract_type: str, 
        user_id: str
    ) -> dict:
        """
        Handle the user's response to a clarification question.
        
        Args:
            user_response: The user's response to the clarification question
            language: Language code ('es' or 'en')
            contract_type: User contract type ('contractor' or 'direct')
            user_id: User identifier
            
        Returns:
            Dictionary with answer, link, and point_of_contact
        """
        try:
            # Get the session state
            session = session_manager.get_session(user_id)
            
            if not session.pending_faqs or not session.last_user_question:
                # No pending clarification, clear and return error
                session_manager.clear_pending_clarification(user_id)
                return self.get_out_of_scope_message(language)
            
            # Build the available FAQs context
            available_faqs_text = []
            for idx, faq_metadata in enumerate(session.pending_faqs):
                faq_question = faq_metadata.get("question", "")
                answer_key = "contractor_answer" if contract_type == "contractor" else "direct_answer"
                faq_answer = faq_metadata.get(answer_key, "")
                
                available_faqs_text.append(
                    f"FAQ {idx}:\n"
                    f"Question: {faq_question}\n"
                    f"Answer: {faq_answer}\n"
                )
            
            available_faqs_context = "\n\n".join(available_faqs_text)
            
            # Create parser for the clarification response output
            parser = PydanticOutputParser(pydantic_object=ClarificationResponseOutput)
            
            # Create the chain
            chain = faq_clarification_response_prompt | CompanyChatbotService.get_one_shot_model() | parser
            
            # Invoke the chain
            clarification_result: ClarificationResponseOutput = chain.invoke({
                "original_question": session.last_user_question,
                "user_response": user_response,
                "available_faqs": available_faqs_context,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Check if we need more clarification
            if clarification_result.needs_more_clarification or clarification_result.confidence < 0.5:
                # Still unclear, ask for more clarification
                if language == 'es':
                    return {
                        "answer": "No estoy seguro de entender tu respuesta. ¿Podrías ser más específico sobre cuál de las opciones necesitas?",
                        "link": "",
                        "point_of_contact": ""
                    }
                else:
                    return {
                        "answer": "I'm not sure I understand your response. Could you be more specific about which option you need?",
                        "link": "",
                        "point_of_contact": ""
                    }
            
            # Check if a FAQ was selected
            if clarification_result.selected_faq_index is not None:
                faq_index = clarification_result.selected_faq_index
                
                # Validate the index
                if 0 <= faq_index < len(session.pending_faqs):
                    metadata = session.pending_faqs[faq_index]
                    
                    # Clear the pending clarification
                    session_manager.clear_pending_clarification(user_id)
                    
                    # Return the selected FAQ answer
                    return {
                        "answer": metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"],
                        "link": metadata["link"],
                        "point_of_contact": metadata["contractor_point_of_contact"] if contract_type == "contractor" else metadata["direct_point_of_contact"]
                    }
            
            # No FAQ selected (user said "none", "neither", etc.)
            session_manager.clear_pending_clarification(user_id)
            return self.get_out_of_scope_message(language)
            
        except Exception as e:
            print(f"[ERROR in handle_clarification_response] {str(e)}")
            # Clear the session and return error message
            session_manager.clear_pending_clarification(user_id)
            return self.get_out_of_scope_message(language)
        
