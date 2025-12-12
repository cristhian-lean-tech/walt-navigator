import os
import asyncio
from typing import Dict, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langdetect import detect
from app.services.langchain import CompanyChatbotService
from app.services.embdding import EmbeddingService
import time
from app.services.prompts import faq_intent_classifier_prompt
from app.services.embdding import CollectionName


MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

class FaqsService2:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.llm = ChatOpenAI(
            temperature=0,
            model=MODEL_NAME,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )        

    def _detect_language(self, text: str) -> str:
        """Detect if the text is in Spanish or English."""
        try:
            detected_lang = detect(text)
            return 'es' if detected_lang == 'es' else 'en'
        except:
            return 'en'

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
        formatted_prompt_value = faq_intent_classifier_prompt.format_prompt(user_input=question)
        formatted_prompt_text = formatted_prompt_value.to_string()
        category_response = CompanyChatbotService.get_one_shot_model().invoke([HumanMessage(content=formatted_prompt_text)])
        
        print(f"[CATEGORY] {category_response.content}")

        if category_response.content == "SMALL_TALK":
            response = CompanyChatbotService.get_small_talk_agent().invoke({
                "messages": [HumanMessage(content=question)]
                },
                config=config
            )
            return response.get("messages", "")[-1].content

        if category_response.content == "IN_SCOPE":
            faqs = self.embedding_service.search_text(
                text=question,
                collection_name=CollectionName.FAQS,
                n_results=2,
                where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]}
            )
            from_db = []
            if faqs["ids"][0] and len(faqs["ids"][0]) > 0:
                high_accuracy = [item for item in faqs if item["distance"] < 0.4]
                if len(high_accuracy) > 0:
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
                    # get the metadata of the lowest distance
                    metadata = high_accuracy[0]["metadata"]
                    faqs
                    return {
                        "answer": metadata["contractor_answer"] if contract_type == "contractor" else metadata["direct_answer"]
                    }
              
            response = faqs_agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
            content = response.get("messages", "")[-1].content
            return content

        if category_response.content == "OUT_OF_SCOPE":
            language = self._detect_language(question)
            return self._get_out_of_scope_message(language)

        return "No response generated"
  
    def interact_with_user(self, question: str, contract_type: str, user_id: str):
        """
        Interacts with the user's question based on the contract type.
        """
        try:
            import threading
            import queue
            
            # Use user_id as thread_id for conversation continuity
            # Set recursion_limit in configurable to prevent infinite loops
            # According to LangGraph docs, recursion_limit should be in configurable
            config = {
                "configurable": {
                    "thread_id": user_id,
                    "recursion_limit": 5  # CRITICAL: Prevent infinite loops - max 5 iterations
                }
            }
            faqs_agent = CompanyChatbotService.get_faqs_agent()
            
            # Use a queue to get response from thread
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def run_agent():
                try:
                    print(f"[AGENT] Starting agent invocation with recursion_limit=5")
                    
                    # Use invoke with proper config
                    # Catch GraphRecursionError which is raised when recursion_limit is exceeded
                    try:
                        response = faqs_agent.invoke(
                            {
                                "messages": [HumanMessage(content=question)]
                            },
                            config=config
                        )
                        result_queue.put(response)
                    except Exception as e:
                        # Check if it's a recursion limit error
                        error_str = str(e).lower()
                        if "recursion" in error_str or "limit" in error_str:
                            print(f"[AGENT] Recursion limit reached: {e}")
                            # Try to extract partial response if available
                            # For now, return a timeout message
                            result_queue.put({
                                "messages": [{"content": "The request exceeded the maximum processing steps. Please try rephrasing your question."}]
                            })
                        else:
                            raise
                except Exception as e:
                    exception_queue.put(e)
            
            # Run agent in a thread with timeout
            agent_thread = threading.Thread(target=run_agent, daemon=True)
            agent_thread.start()
            agent_thread.join(timeout=30)  # 30 second timeout
            
            if agent_thread.is_alive():
                print("[AGENT] Timeout reached after 30 seconds, forcing return")
                return {
                    "answer": "I apologize, but the request took too long to process. Please try rephrasing your question or contact support.",
                    "link": "",
                    "point_of_contact": ""
                }
            
            # Check for exceptions
            if not exception_queue.empty():
                exception_occurred = exception_queue.get()
                raise exception_occurred
            
            # Get response
            if result_queue.empty():
                raise Exception("Agent returned no response")
            
            response = result_queue.get()
            print("[OUT]", response)
            
            # Extract the response from the agent output
            # Since we're using ToolStrategy(FaqsResponseDTO), the response should be structured
            if isinstance(response, dict):
                # Check if response has the structured format
                if "messages" in response:
                    messages = response["messages"]
                    # Get the last message which should be the agent's response
                    if messages:
                        last_message = messages[-1]
                        # Check if it's a structured output (AIMessage with tool_calls or content)
                        if hasattr(last_message, "content"):
                            content = last_message.content
                            # If content is a dict (structured output), extract fields
                            if isinstance(content, dict):
                                answer = content.get("answer", str(content))
                                link = content.get("link", "")
                                point_of_contact = content.get("point_of_contact", "")
                            else:
                                answer = str(content) if content else "No response generated"
                                link = ""
                                point_of_contact = ""
                        else:
                            answer = str(last_message)
                            link = ""
                            point_of_contact = ""
                    else:
                        answer = "No response generated"
                        link = ""
                        point_of_contact = ""
                # Check if response is already in the expected format
                elif "answer" in response:
                    answer = response["answer"]
                    link = response.get("link", "")
                    point_of_contact = response.get("point_of_contact", "")
                else:
                    # Fallback: convert entire response to string
                    answer = str(response)
                    link = ""
                    point_of_contact = ""
            else:
                answer = str(response)
                link = ""
                point_of_contact = ""
            
            # Return in expected format
            return {
                "answer": answer,
                "link": link,
                "point_of_contact": point_of_contact
            }
        except Exception as e:
            import traceback
            print(f"[ERROR] Agent invocation failed: {e}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            # Return error response
            return {
                "answer": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "link": "",
                "point_of_contact": ""
            }