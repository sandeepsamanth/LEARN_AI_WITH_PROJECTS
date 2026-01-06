"""
Euron Embeddings API Utility
Uses Euron API for generating embeddings
"""
from typing import List
import numpy as np
import json
import requests
from app.core.config import settings


class EmbeddingGenerator:
    """Generate embeddings using Euron API"""
    
    def __init__(self):
        self.api_key = settings.EURON_API_KEY
        self.api_url = settings.EURON_API_URL
        self.model = settings.EURON_EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Euron API
        
        Args:
            text: Input text string
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.model
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract embedding from response
            # Euron API response format: {"data": [{"embedding": [...]}]}
            embedding = None
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                    embedding = data["data"][0].get("embedding", [])
                elif "embedding" in data:
                    embedding = data["embedding"]
            elif isinstance(data, list) and len(data) > 0:
                embedding = data[0].get("embedding", []) if isinstance(data[0], dict) else []
            
            if not embedding:
                raise ValueError(f"No embedding returned from API. Response: {data}")
            
            return embedding
            
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input text strings
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding for text: {str(e)}")
                # Return zero vector as fallback
                embeddings.append([0.0] * self.dimension)
        return embeddings
    
    def embedding_to_json(self, embedding: List[float]) -> str:
        """Convert embedding list to JSON string (for backward compatibility)"""
        return json.dumps(embedding)
    
    def json_to_embedding(self, json_str: str) -> List[float]:
        """Convert JSON string to embedding list (for backward compatibility)"""
        if isinstance(json_str, str):
            return json.loads(json_str)
        return json_str  # Already a list
    
    def to_pgvector(self, embedding: List[float]):
        """Convert embedding to format suitable for pgvector (returns as-is, pgvector handles it)"""
        return embedding
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Global instance
embedding_generator = EmbeddingGenerator()







