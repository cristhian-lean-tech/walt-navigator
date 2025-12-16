import json
from typing import Dict, Optional, Any, List
from app.shared.const import CollectionName
from .embdding import EmbeddingService
from .prompts import benefit_route_prompt
from app.services.langchain import CompanyChatbotService

class ConversationService():

    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    def process_user_input(self, content: str, user_type: str, user_id: str) -> Dict[str, Any]:
        benefit_route = self.embedding_service.search_text(
            text=content,
            collection_name=CollectionName.NAVIGATION,
            where={"$or": [{"user_type": user_type}, {"user_type": "any"}]}
        )

        
        benefit_route = self._parse_response(benefit_route)
        chain = benefit_route_prompt | CompanyChatbotService.get_one_shot_model()
        response = chain.invoke({"matches": json.dumps(benefit_route, indent=2)})

        result = json.loads(response.content)
        
        response = {
            "response": result.get("message"),
            "paths": benefit_route or None,
            "request_type": ""
        }

        return response
    
    def _parse_response(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output = []
        for id_value, metadata, distance in zip(results["ids"][0], results["metadatas"][0], results["distances"][0]):
            output.append({
                  "path": id_value,
                  "description": metadata["short_description"],
                  "score": round((1-distance), 2)
            })
         
        return output


