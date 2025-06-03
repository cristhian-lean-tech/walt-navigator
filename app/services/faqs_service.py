from app.services.embdding import EmbeddingService
from app.shared.onboarding_faqs import ONBOARDING_FAQS
from app.shared.const import CollectionName

class FaqsService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def response_faqs(self, question: str, contract_type: str):
        if(question.strip() == ""):
            return "I'm sorry, I didn't understand your question. Please try again."
        
        faqs = self.embedding_service.search_text(
            text=question,
            collection_name=CollectionName.FAQS,
            where={"$or": [{"user_type": contract_type}, {"user_type": "both"}]},
            n_results=1
        )
        output = []
        for id_value, metadata, distance in zip(faqs["ids"][0], faqs["metadatas"][0], faqs["distances"][0]):
            print(distance)
            if(distance < 0.5):
                output.append({
                    "question": id_value,
                    "answer": "No answer found",
                    "link": "",
                    "point_of_contact": ""
                })
            else:
                output.append({
                    "question": id_value,
                    "answer": metadata["answer"],
                    "link": metadata["link"],
                    "point_of_contact": metadata["point_of_contact"]
                })
         
        if(len(output) == 0):
            return "I'm sorry, I didn't find any information about that. Please try again."
        
        return output[0]