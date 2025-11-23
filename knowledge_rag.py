"""
Sistema RAG Clásico para Base de Conocimiento de Salud Mental
Responde preguntas como "¿Qué hago?" o "¿Por qué me siento así?"

Técnica: RAG Clásico con similitud coseno
- Top 1 suele ser suficiente para demos
- Sin reranking complejo
"""

import json
import os
import numpy as np
from typing import Dict, Any, List, Optional
from openai import OpenAI
import faiss
import pickle
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class MentalHealthKnowledgeRAG:
    """
    Sistema RAG para consultas sobre conocimiento de salud mental
    Usa OpenAI embeddings + FAISS para búsqueda rápida
    """
    
    def __init__(self,
                 knowledge_base_path: str = 'base_conocimiento_rag_pasos_inmediatos.json',
                 openai_model: str = 'text-embedding-3-small',
                 index_path: str = 'faiss_pasos/knowledge_index.bin',
                 metadata_path: str = 'faiss_pasos/knowledge_metadata.pkl',
                 force_rebuild: bool = False):
        """
        Inicializa el sistema RAG de conocimiento
        
        Args:
            knowledge_base_path: Ruta al JSON con la base de conocimiento
            openai_model: Modelo de embeddings de OpenAI
            index_path: Ruta para guardar/cargar índice FAISS
            metadata_path: Ruta para guardar/cargar metadatos
            force_rebuild: Si True, regenera embeddings aunque exista cache
        """
        # Cargar base de conocimiento
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)
        
        # Configurar OpenAI
        self.openai_model = openai_model
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise EnvironmentError('OPENAI_API_KEY no está definido en las variables de entorno')
        self.client = OpenAI(api_key=api_key)
        
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else '.', exist_ok=True)
        os.makedirs(os.path.dirname(metadata_path) if os.path.dirname(metadata_path) else '.', exist_ok=True)
        
        # Intentar cargar desde cache
        if not force_rebuild and os.path.exists(index_path) and os.path.exists(metadata_path):
            print("Cargando base de conocimiento desde cache")
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                cached_data = pickle.load(f)
                self.knowledge_base = cached_data['knowledge_base']
            print(f"Base de conocimiento cargada: {self.index.ntotal} articulos")
        else:
            print("Generando embeddings para base de conocimiento")
            embeddings = self._generate_embeddings()
            
            # Crear índice FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalizar vectores para cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            # Guardar cache
            print(f"Guardando cache en {self.index_path}")
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({'knowledge_base': self.knowledge_base}, f)
            print("Cache guardado")
        
        print(f"Sistema RAG listo con {len(self.knowledge_base)} articulos de conocimiento")
    
    def _create_searchable_text(self, article: Dict[str, Any]) -> str:
        """
        Crea texto enriquecido del artículo para embeddings
        Incluye tema, síntomas, descripción, pasos, etc.
        """
        parts = [
            article.get('tema', ''),
            article.get('categoria', ''),
            article.get('descripcion_clinica', ''),
        ]
        
        # Síntomas clave (muy importante para matching)
        if 'sintomas_clave' in article:
            parts.append(' '.join(article['sintomas_clave']))
        
        # Síntomas específicos según tipo
        for key in ['sintomas_manias', 'sintomas_depresion', 'sintomas_tempranos', 'sintomas_psicosis_clara']:
            if key in article:
                parts.append(' '.join(article[key]))
        
        # Señales de alerta
        if 'senales_de_alerta_graves' in article:
            parts.append(' '.join(article['senales_de_alerta_graves']))
        
        # Pasos inmediatos (descripción de acciones)
        if 'pasos_inmediatos' in article:
            for paso in article['pasos_inmediatos']:
                if isinstance(paso, dict):
                    parts.append(paso.get('nombre', ''))
                    parts.append(paso.get('descripcion', ''))
                    parts.append(paso.get('accion', ''))
                    parts.append(paso.get('detalles', ''))
        
        # Técnicas específicas
        if 'tecnicas_grounding' in article:
            for tecnica in article['tecnicas_grounding']:
                parts.append(tecnica.get('nombre', ''))
                if 'pasos' in tecnica:
                    parts.append(' '.join(tecnica['pasos']))
        
        # Nivel de urgencia
        parts.append(article.get('nivel_urgencia', ''))
        
        return ' '.join([str(p) for p in parts if p])
    
    def _generate_embeddings(self) -> np.ndarray:
        """Genera embeddings para toda la base de conocimiento"""
        texts = [self._create_searchable_text(art) for art in self.knowledge_base]
        
        print(f"Procesando {len(texts)} articulos")
        resp = self.client.embeddings.create(model=self.openai_model, input=texts)
        embeddings = np.array([d.embedding for d in resp.data], dtype='float32')
        print("Embeddings generados")
        
        return embeddings
    
    def ask(self, 
            question: str, 
            top_k: int = 1,
            include_context: bool = True) -> List[Dict[str, Any]]:
        """
        Responde una pregunta buscando en la base de conocimiento
        
        Args:
            question: Pregunta del usuario ("¿Qué hago si tengo ansiedad?")
            top_k: Número de artículos a retornar (default: 1)
            include_context: Si True, incluye contexto completo del artículo
            
        Returns:
            Lista de artículos relevantes con scores de similitud
        """
        # Generar embedding de la pregunta
        resp = self.client.embeddings.create(model=self.openai_model, input=[question])
        query_embedding = np.array(resp.data[0].embedding, dtype='float32').reshape(1, -1)
        
        # Normalizar para cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Buscar en FAISS
        similarities, indices = self.index.search(query_embedding, top_k)
        
        # Construir resultados
        results = []
        for idx, similarity in zip(indices[0], similarities[0]):
            article = self.knowledge_base[idx].copy()
            article['similarity_score'] = float(similarity)
            article['relevancia'] = self._classify_relevance(similarity)
            
            # Opcionalmente reducir contexto
            if not include_context:
                # Solo incluir campos esenciales
                article = {
                    'id': article.get('id'),
                    'tema': article.get('tema'),
                    'categoria': article.get('categoria'),
                    'nivel_urgencia': article.get('nivel_urgencia'),
                    'similarity_score': article['similarity_score'],
                    'relevancia': article['relevancia']
                }
            
            results.append(article)
        
        return results
    
    def _classify_relevance(self, similarity: float) -> str:
        """Clasifica la relevancia basada en el score de similitud"""
        if similarity >= 0.85:
            return "Muy Alta"
        elif similarity >= 0.75:
            return "Alta"
        elif similarity >= 0.65:
            return "Media"
        else:
            return "Baja"
    
    def get_emergency_response(self) -> Dict[str, Any]:
        """
        Retorna respuesta de emergencia para crisis
        Busca artículo con nivel_urgencia CRÍTICO
        """
        for article in self.knowledge_base:
            if article.get('nivel_urgencia', '').upper() == 'CRÍTICO':
                return article
        
        # Fallback genérico
        return {
            'tema': 'EMERGENCIA - Contacta ayuda inmediata',
            'NUMEROS_EMERGENCIA': {
                'México': '800-911-2000 (24/7 GRATIS)',
                'Internacional': '911'
            }
        }
    
    def search_by_symptoms(self, symptoms: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca artículos por síntomas específicos
        
        Args:
            symptoms: Lista de síntomas ["ansiedad", "taquicardia", "sudoración"]
            top_k: Número de resultados
            
        Returns:
            Artículos ordenados por relevancia
        """
        query = ' '.join(symptoms)
        return self.ask(query, top_k=top_k, include_context=True)
    
    def format_response(self, article: Dict[str, Any], include_sources: bool = True) -> str:
        """
        Formatea un artículo de conocimiento como respuesta legible
        
        Args:
            article: Artículo de la base de conocimiento
            include_sources: Si incluir fuentes y enlaces
            
        Returns:
            Texto formateado para mostrar al usuario
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(f"{article.get('tema', 'Información')}")
        lines.append("=" * 60)
        
        # Categoría y urgencia
        categoria = article.get('categoria', 'General')
        urgencia = article.get('nivel_urgencia', 'N/A')
        lines.append(f"\nCategoria: {categoria}")
        lines.append(f"Nivel de Urgencia: {urgencia}")
        
        # Descripción clínica
        if 'descripcion_clinica' in article:
            lines.append(f"\nDescripcion:")
            lines.append(f"   {article['descripcion_clinica']}")
        
        # Síntomas clave
        if 'sintomas_clave' in article:
            lines.append(f"\nSintomas Clave:")
            for sintoma in article['sintomas_clave']:
                lines.append(f"   - {sintoma}")
        
        # Pasos inmediatos
        pasos_key = 'PASOS_INMEDIATOS_CRÍTICOS' if 'PASOS_INMEDIATOS_CRÍTICOS' in article else 'pasos_inmediatos'
        if pasos_key in article:
            lines.append(f"\nPasos Inmediatos:")
            for paso in article[pasos_key]:
                if isinstance(paso, dict):
                    paso_num = paso.get('paso', '')
                    nombre = paso.get('nombre', paso.get('accion', ''))
                    desc = paso.get('descripcion', paso.get('detalles', ''))
                    lines.append(f"\n   {paso_num}. {nombre}")
                    if desc:
                        lines.append(f"      {desc}")
        
        # Números de emergencia si es crítico
        if urgencia == 'CRÍTICO' and 'NUMEROS_EMERGENCIA' in article:
            lines.append(f"\nNUMEROS DE EMERGENCIA:")
            for pais, numero in article['NUMEROS_EMERGENCIA'].items():
                lines.append(f"   {pais}: {numero}")
        
        # Fuentes
        if include_sources and 'fuentes' in article:
            lines.append(f"\nFuentes: {', '.join(article['fuentes'])}")
        
        # Score de similitud
        if 'similarity_score' in article:
            score = article['similarity_score']
            relevancia = article.get('relevancia', 'N/A')
            lines.append(f"\nRelevancia: {relevancia} ({score:.3f})")
        
        lines.append("\n" + "=" * 60)
        
        return '\n'.join(lines)


if __name__ == '__main__':
    # Sistema listo para ser importado y usado por el API
    pass
