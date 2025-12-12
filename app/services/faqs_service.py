import os
from typing import Dict, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langdetect import detect
from deep_translator import GoogleTranslator
from app.services.langchain import CompanyChatbotService
from app.services.embdding import EmbeddingService
from app.shared.const import CollectionName
from app.services.prompts import (
    faq_intent_classifier_prompt,
    faq_conversational_prompt,
    faq_followup_prompt
)

MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

class FaqsService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm = ChatOpenAI(
            temperature=0,
            model=MODEL_NAME,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        # Intent classifier chain
        self.intent_classifier = LLMChain(
            llm=self.llm,
            prompt=faq_intent_classifier_prompt
        )
        # Conversational memory storage per user_id
        self.conversation_memories: Dict[str, ConversationBufferMemory] = {}
        # Conversational chains per user_id
        self.conversation_chains: Dict[str, ConversationChain] = {}

    def _detect_language(self, text: str) -> str:
        """Detect if the text is in Spanish or English."""
        try:
            detected_lang = detect(text)
            return 'es' if detected_lang == 'es' else 'en'
        except:
            return 'en'

    def _get_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for a user."""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationBufferMemory(
                memory_key="history"
            )
        return self.conversation_memories[user_id]

    def _get_conversation_chain(self, user_id: str) -> ConversationChain:
        """Get or create conversation chain for a user."""
        if user_id not in self.conversation_chains:
            memory = self._get_memory(user_id)
            self.conversation_chains[user_id] = ConversationChain(
                llm=self.llm,
                memory=memory,
                prompt=faq_conversational_prompt,
                verbose=False
            )
        return self.conversation_chains[user_id]

    def _classify_intent(self, question: str) -> str:
        """Classify user intent: IN_SCOPE, OUT_OF_SCOPE, or SMALL_TALK."""
        try:
            result = self.intent_classifier.invoke({"user_input": question})
            intent = result["text"].strip().upper()
            # Normalize intent
            if "IN_SCOPE" in intent or "IN-SCOPE" in intent:
                return "IN_SCOPE"
            elif "OUT_OF_SCOPE" in intent or "OUT-OF-SCOPE" in intent:
                return "OUT_OF_SCOPE"
            elif "SMALL_TALK" in intent or "SMALL-TALK" in intent:
                return "SMALL_TALK"
            else:
                # Default to IN_SCOPE if unclear
                return "IN_SCOPE"
        except Exception as e:
            # Default to IN_SCOPE on error
            return "IN_SCOPE"

    def _get_out_of_scope_message(self, language: str) -> dict:
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

    def _get_small_talk_response(self, question: str, user_id: str, language: str) -> dict:
        """Generate conversational response for small talk."""
        conversation_chain = self._get_conversation_chain(user_id)
        try:
            response = conversation_chain.run(input=question)
            return {
                "answer": response,
                "link": "",
                "point_of_contact": ""
            }
        except Exception as e:
            # Fallback responses
            fallback_messages = {
                'es': {
                    "hola": "¡Hola! ¿En qué puedo ayudarte hoy?",
                    "gracias": "¡De nada! Estoy aquí para ayudarte cuando lo necesites.",
                    "default": "¡Hola! ¿Tienes alguna pregunta sobre soporte, beneficios o políticas de la empresa?"
                },
                'en': {
                    "hello": "Hello! How can I help you today?",
                    "thanks": "You're welcome! I'm here to help whenever you need.",
                    "default": "Hello! Do you have any questions about support, benefits, or company policies?"
                }
            }
            question_lower = question.lower()
            if "hola" in question_lower or "hi" in question_lower or "hello" in question_lower:
                key = "hola" if language == 'es' else "hello"
            elif "gracias" in question_lower or "thank" in question_lower:
                key = "gracias" if language == 'es' else "thanks"
            else:
                key = "default"
            
            return {
                "answer": fallback_messages[language][key],
                "link": "",
                "point_of_contact": ""
            }

    def _get_no_answer_message(self, language: str) -> str:
        """Return appropriate 'no answer found' message based on language."""
        messages = {
            'es': "🤔 Hmm, no pude encontrar una buena respuesta para eso aún!",
            'en': "🤔 Hmm, I couldn't find a good answer for that just yet!"
        }
        return messages.get(language, messages['en'])

    def _get_conversational_followup(self, question: str, user_id: str, language: str) -> str:
        """Generate conversational follow-up when RAG doesn't find good results."""
        memory = self._get_memory(user_id)
        # Get chat history from memory
        try:
            # ConversationBufferMemory stores history in buffer attribute
            chat_history = memory.buffer if hasattr(memory, 'buffer') and memory.buffer else ""
        except:
            chat_history = ""
        
        followup_chain = LLMChain(
            llm=self.llm,
            prompt=faq_followup_prompt
        )
        
        try:
            response = followup_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            return response["text"]
        except Exception as e:
            # Fallback message
            messages = {
                'es': "No encontré información específica sobre eso. ¿Podrías reformular tu pregunta o proporcionar más detalles?",
                'en': "I didn't find specific information about that. Could you rephrase your question or provide more details?"
            }
            return messages.get(language, messages['en'])

    def _not_found_message(self, language: str, question: str = "", user_id: str = "") -> dict:
        """Return message when no information is found, with conversational context."""
        if user_id:
            answer = self._get_conversational_followup(question, user_id, language)
        else:
            not_found_messages = {
                'es': "Lo siento, no encontré información sobre eso. Por favor intenta de nuevo.",
                'en': "I'm sorry, I didn't find any information about that. Please try again."
            }
            answer = not_found_messages.get(language, not_found_messages['en'])
    
        return {
            "answer": answer,
            "link": "",
            "point_of_contact": ""
        }
    
    def response_faqs(self, question: str, contract_type: str, user_id: str):
        """
        Process FAQ question with intent classification and conversational memory.
        
        Args:
            question: User's question
            contract_type: Type of contract (contractor/direct)
            user_id: User ID (used as conversation_id for memory)
        
        Returns:
            dict with answer, link, and point_of_contact
        """
        # Validate question
        if question.strip() == "":
            language = self._detect_language(question)
            empty_messages = {
                'es': "Lo siento, no entendí tu pregunta. Por favor intenta de nuevo.",
                'en': "I'm sorry, I didn't understand your question. Please try again."
            }
            return {
                "answer": empty_messages.get(language, empty_messages['en']),
                "link": "",
                "point_of_contact": ""
            }
        
        # Detect language
        language = self._detect_language(question)
        
        # Classify intent
        intent = self._classify_intent(question)
        
        # Handle different intents
        if intent == "OUT_OF_SCOPE":
            # Store in memory for context
            memory = self._get_memory(user_id)
            memory.save_context({"input": question}, {"output": "OUT_OF_SCOPE"})
            return self._get_out_of_scope_message(language)
        
        elif intent == "SMALL_TALK":
            response = self._get_small_talk_response(question, user_id, language)
            # Store in memory
            memory = self._get_memory(user_id)
            memory.save_context({"input": question}, {"output": response["answer"]})
            return response
        
        # IN_SCOPE: Proceed with RAG search
        faqs = self.embedding_service.search_text(
            text=question,
            collection_name=CollectionName.FAQS,
            where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]},
            n_results=1
        )
        
        output = []
        if faqs["ids"][0] and len(faqs["ids"][0]) > 0:
            for id_value, metadata, distance in zip(faqs["ids"][0], faqs["metadatas"][0], faqs["distances"][0]):
                if distance > 0.4:
                    # Low similarity - use conversational follow-up
                    answer = self._get_conversational_followup(question, user_id, language)
                    output.append({
                        "question": id_value,
                        "answer": answer,
                        "link": "",
                        "point_of_contact": ""
                    })
                else:
                    # Good match - return RAG answer
                    answer_key = "contractor_answer" if contract_type == "contractor" else "direct_answer"
                    point_of_contact_key = "contractor_point_of_contact" if contract_type == "contractor" else "direct_point_of_contact"
                    answer = metadata[answer_key]
                    
                    # Translate if needed
                    if language == 'es' and self._detect_language(answer) == 'en':
                        answer = GoogleTranslator(source='en', target='es').translate(answer)
                    
                    output.append({
                        "question": id_value,
                        "answer": answer,
                        "link": metadata.get("link", ""),
                        "point_of_contact": metadata.get(point_of_contact_key, "")
                    })
        
        # No results found
        if len(output) == 0:
            return self._not_found_message(language, question, user_id)
        
        # Store successful interaction in memory
        memory = self._get_memory(user_id)
        memory.save_context(
            {"input": question},
            {"output": output[0]["answer"]}
        )
        
        return output[0]
    
    def interact_with_user(self, question: str, contract_type: str, user_id: str):
        """
        Interacts with the user's question based on the contract type.
        """
        company_chatbot_service = CompanyChatbotService()
        response = company_chatbot_service.faqs_agent.invoke({"question": question, "contract_type": contract_type, "user_id": user_id})
        return response