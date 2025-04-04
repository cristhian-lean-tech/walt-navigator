import json
from typing import Dict, List, Optional
from numpy import dot
from numpy.linalg import norm

from app.shared.const import CollectionName
from .embdding import EmbeddingService
from .text_normalizer import TextNormalizer
from app.shared.paths import PATHS
from app.shared.forms import FORMS

class NavigationService():
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.text_normalizer = TextNormalizer()
        self.benefit_embeddings = {}
        self.benefit_synonyms = self._init_benefit_synonyms()
        self._init_benefit_embeddings()  # Inicializar embeddings al crear la instancia

    def suggest_routes(self, content: str, role: str) -> any:
        # Normalizar el texto de entrada
        normalized_content = self.text_normalizer.normalize(content)
        print("**** 1", normalized_content)
        
        # Obtener palabras clave
        keywords = self.text_normalizer.get_keywords(normalized_content)
        print("**** 3", keywords)
        
        # Buscar en la base de datos vectorial
        result = self.embedding_service.search_text(normalized_content, CollectionName.NAVIGATION)
        print("**** 4", result)

        # Detectar beneficio usando múltiples métodos
        detected_benefit = self._detect_benefit_combined(normalized_content, keywords)
        print("**** 5", detected_benefit)
        
        if detected_benefit:
            return {"message": f"Great! You're requesting {detected_benefit}. Let's start. When would you like to begin?"}

        print("**** 6")
        return result
    
    def init_database(self):
        databseWasInitialized = self.embedding_service.exists_collection(CollectionName.NAVIGATION)
        if databseWasInitialized:
            return
        
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        ids = [item["path"] for item in PATHS]
        documents = [item["description"] for item in PATHS]
        metadatas = [{"description": item["description"]} for item in PATHS]

        collection.add(
            ids=ids,
            embeddings=[self.embedding_service.generate_embedding(doc) for doc in documents],
            metadatas=metadatas
        )

        self._init_benefit_embeddings()
    
    def cleanup_database(self):
        collection = self.embedding_service.get_collection(CollectionName.NAVIGATION)
        collection.delete()

    def _init_benefit_synonyms(self) -> Dict[str, List[str]]:
        """
        Inicializa un diccionario de sinónimos para cada beneficio.
        """
        synonyms = {}
        for benefit in FORMS.keys():
            # Agregar el beneficio original
            synonyms[benefit] = [benefit]
            
            # Agregar sinónimos usando el normalizador
            normalized_benefit = self.text_normalizer.normalize(benefit)
            benefit_synonyms = self.text_normalizer.get_synonyms(normalized_benefit)
            synonyms[benefit].extend(benefit_synonyms)
            
            # Agregar variaciones comunes
            if "vacation" in benefit:
                synonyms[benefit].extend(["holiday", "time off", "leave"])
            elif "gym" in benefit:
                synonyms[benefit].extend(["fitness", "workout", "exercise"])
            elif "days off" in benefit:
                synonyms[benefit].extend(["day off", "personal day", "time off"])
        
        return synonyms

    def _detect_benefit_combined(self, content: str, keywords: List[str]) -> Optional[str]:
        """
        Combina múltiples métodos para detectar beneficios de manera más robusta.
        """
        # 1. Detección por palabras clave (más confiable para español)
        for benefit, synonyms in self.benefit_synonyms.items():
            # Verificar si alguna palabra clave coincide con los sinónimos
            if any(keyword in synonyms for keyword in keywords):
                return benefit

        # 2. Detección por similitud semántica (si hay embeddings disponibles)
        if self.benefit_embeddings:
            semantic_match = self._semantic_detect_benefit(content)
            if semantic_match:
                return semantic_match

        # 3. Detección por coincidencia exacta
        for benefit in FORMS.keys():
            if benefit in content:
                return benefit

        return None

    def _semantic_detect_benefit(self, content: str) -> Optional[str]:
        """
        Detecta beneficios usando similitud semántica con embeddings.
        """
        if not self.benefit_embeddings:
            return None

        query_embedding = self.embedding_service.generate_embedding(content)

        def cosine_similarity(a, b):
            return dot(a, b) / (norm(a) * norm(b))

        scores = {
            benefit: cosine_similarity(query_embedding, emb)
            for benefit, emb in self.benefit_embeddings.items()
        }

        if not scores:
            return None

        best_match, best_score = max(scores.items(), key=lambda x: x[1])
        return best_match if best_score > 0.65 else None

    def _detect_benefit(self, content: str) -> str or None:
        for benefit in FORMS.keys():
           if benefit in content.lower():
               return benefit            
        return None

    def _init_benefit_embeddings(self):
        from app.shared.forms import FORMS
        self.benefit_embeddings = {
            benefit: self.embedding_service.generate_embedding(benefit)
            for benefit in FORMS.keys()
        }

#  Fase 1: Mejorar la detección de beneficios
# ✅ Usar embeddings en lugar de palabras clave (_detect_benefit) para detectar intenciones más naturalmente.
# ⬆️ Hacer que reconozca sinónimos, errores ortográficos o frases largas.
# 💬 Fase 2: Flujos conversacionales dinámicos
# ✅ Cada beneficio puede tener parámetros (como fechas, tipo de solicitud, etc).
# 🔁 Hacer preguntas personalizadas según el beneficio detectado.
# 💾 Guardar respuestas en sesión temporal (en memoria por ahora).
# 📝 Fase 3: Registro de solicitudes
# 🗃 Guardar cada solicitud en base de datos o archivo (quién pidió qué y cuándo).
# 🕵️‍♀️ Auditar peticiones o generar reportes.
# 🤖 Fase 4: Integraciones externas
# 💬 Integrar con Slack, WhatsApp o frontend Web con botones.
# 🔔 Notificaciones automáticas o correos.
# 📦 Fase 5: Despliegue y monitoreo
# 🐳 Docker funcional.
# 🚦 Health checks y logs.
# 📊 Métricas básicas del sistema.