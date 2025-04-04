import re
from typing import List
from unidecode import unidecode

class TextNormalizer:
    def __init__(self):
        # Diccionario de sinónimos básico
        self.synonyms = {
            "vacation": ["vacaciones", "tiempo libre", "descanso", "receso"],
            "gym": ["gimnasio", "ejercicio", "fitness", "entrenamiento"],
            "days off": ["dias libres", "dias personales", "tiempo personal"]
        }

    def normalize(self, text: str) -> str:
        """
        Normaliza el texto para mejorar la detección de beneficios.
        """
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos
        text = unidecode(text)
        
        # Remover caracteres especiales y números
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remover espacios extra
        text = ' '.join(text.split())
        
        return text

    def get_keywords(self, text: str) -> List[str]:
        """
        Extrae palabras clave del texto.
        """
        # Dividir el texto en palabras
        words = text.split()
        
        # Filtrar palabras muy cortas
        keywords = [word for word in words if len(word) > 2]
        
        return keywords

    def get_synonyms(self, word: str) -> List[str]:
        """
        Obtiene sinónimos de una palabra usando el diccionario local.
        """
        # Buscar en el diccionario de sinónimos
        for key, synonyms in self.synonyms.items():
            if word in synonyms or word == key:
                return synonyms
        return [word] 