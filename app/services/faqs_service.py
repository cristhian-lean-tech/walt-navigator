from app.services.embdding import EmbeddingService
from app.shared.const import CollectionName
from langdetect import detect
from deep_translator import GoogleTranslator

class FaqsService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def _detect_language(self, text: str) -> str:
        """Detect if the text is in Spanish or English."""
        try:
            detected_lang = detect(text)
            return 'es' if detected_lang == 'es' else 'en'
        except:
            return 'en'

    def _get_no_answer_message(self, language: str) -> str:
        """Return appropriate 'no answer found' message based on language."""
        messages = {
            'es': "🤔 Hmm, no pude encontrar una buena respuesta para eso aún!",
            'en': "🤔 Hmm, I couldn't find a good answer for that just yet!"
        }
        return messages.get(language, messages['en'])

    def _not_found_message(self, language: str) -> dict:
        not_found_messages = {
        'es': "Lo siento, no encontré información sobre eso. Por favor intenta de nuevo.",
        'en': "I'm sorry, I didn't find any information about that. Please try again."
        }
    
        return {
            "answer": not_found_messages.get(language, not_found_messages['en']),
            "link": "",
            "point_of_contact": ""
        }
    
    def response_faqs(self, question: str, contract_type: str):
        if(question.strip() == ""):
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
        
        # Detect the language of the question
        language = self._detect_language(question)
        
        faqs = self.embedding_service.search_text(
            text=question,
            collection_name=CollectionName.FAQS,
            where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]},
            n_results=1
        )
        output = []
        for id_value, metadata, distance in zip(faqs["ids"][0], faqs["metadatas"][0], faqs["distances"][0]):
            if(distance > 0.4):
                output.append({
                    "question": id_value,
                    "answer": self._get_no_answer_message(language),
                    "link": "",
                    "point_of_contact": ""
                })
            else:
                answer_key = "contractor_answer" if contract_type == "contractor" else "direct_answer"
                point_of_contact_key = "contractor_point_of_contact" if contract_type == "contractor" else "direct_point_of_contact"
                answer = metadata[answer_key]
                if language == 'es' and self._detect_language(answer) == 'en':
                    answer = GoogleTranslator(source='en', target='es').translate(answer)
                
                output.append({
                    "question": id_value,
                    "answer": answer,
                    "link": metadata["link"],
                    "point_of_contact": metadata[point_of_contact_key]
                })
         
        if(len(output) == 0):
            return self._not_found_message(language)
        
        return output[0]
    
