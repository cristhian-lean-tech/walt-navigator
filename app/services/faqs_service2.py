import os
import asyncio
from typing import Dict, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langdetect import detect
from app.dtos.faqs import IntentClassifierOutput
from app.services.langchain import CompanyChatbotService
from app.services.embdding import EmbeddingService
import time
from app.services.prompts import faq_intent_classifier_prompt, faq_small_talk_prompt
from app.services.embdding import CollectionName
from langchain_core.output_parsers import PydanticOutputParser

MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

class FaqsService2:
    def __init__(self):
        self.embedding_service = EmbeddingService()

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
    
    def _detect_language(self, text: str) -> str:
        """Detect if the text is in Spanish or English."""
        try:
            detected_lang = detect(text)
            return 'es' if detected_lang == 'es' else 'en'
        except:
            return 'en'

    def ask_faqs_agent(self, question: str, contract_type: str, user_id: str):
        faqs_agent = CompanyChatbotService.get_faqs_agent()
        config = {  
            "configurable": {
                "thread_id": user_id,
                "recursion_limit": 5
            }
        }

        parser = PydanticOutputParser(pydantic_object=IntentClassifierOutput)        
        chain = faq_intent_classifier_prompt | CompanyChatbotService.get_one_shot_model() | parser
        category_response: IntentClassifierOutput = chain.invoke({
            "user_message": question,
            "format_instructions": parser.get_format_instructions()
        })
        intent = category_response.intent
        print(f"[INTENT] {intent}")

        if category_response.intent == "SMALL_TALK":
            small_talk_chain = chain = faq_small_talk_prompt | CompanyChatbotService.get_one_shot_model()
            small_talk_response = small_talk_chain.invoke({
                "user_input": question
            })

            content = small_talk_response.content
            
            return content

        if category_response.intent == "IN_SCOPE":
            faqs = self.embedding_service.search_text(
                text=question,
                collection_name=CollectionName.FAQS,
                n_results=2,
                where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]}
            )
            print(f"[FAQS] {faqs}")

            if faqs["ids"][0] and len(faqs["ids"][0]) > 0:
                print(f"[IF]")
                distances = faqs.get("distances", None)
                print(f"[DISTANCES] {distances}")
                if not distances:
                    #TODO: Handle this case
                    return "No response generated"

                high_accuracy = [item for item in distances[0] if item < 0.4]
                print(f"[HIGH ACCURACY] {high_accuracy}")
                if len(high_accuracy) > 0:
                    print(f"[IF] 2")
                    # get the metadata of the highest distance
                    metadata = high_accuracy[0]["metadata"]
                    answer = metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"]
                    link = metadata["link"]
                    point_of_contact = metadata["contractor_point_of_contact"] if contract_type == "contractor" else metadata["direct_point_of_contact"]
                    return {
                        "answer": answer,
                        "link": link,
                        "point_of_contact": point_of_contact
                    }
                else:
                    print(f"[ELSE 2]")
                    # get the metadata of the lowest distance
                    metadata = high_accuracy[0]["metadata"]
              
                    return {
                        "answer": metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"]
                    }
              
            response = faqs_agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
            content = response.get("messages", "")[-1].content
            return content

        if category_response.intent == "OUT_OF_SCOPE":
            language = self._detect_language(question)
            return self._get_out_of_scope_message(language)

        return "No response generated"
