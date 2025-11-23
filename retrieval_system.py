"""
Sistema de Retrieval RAG para Especialistas de Salud Mental
Proyecto: Aplicación Móvil de Apoyo Mental con IA

Este sistema permite buscar y recomendar los mejores especialistas basándose en:
- Búsqueda semántica con embeddings
- Filtros específicos (costo, modalidad, ubicación, especializaciones)
- Scoring híbrido considerando relevancia, rating, costo y disponibilidad
"""

import json
import os
import time
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from openai import OpenAI
import faiss
import pickle
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


@dataclass
class QueryFilters:
    """Filtros opcionales para la búsqueda de especialistas"""
    max_cost: Optional[float] = None
    min_rating: Optional[float] = None
    modalidad: Optional[List[str]] = None  # ["Presencial", "Online"]
    tipo_profesional: Optional[List[str]] = None
    delegacion: Optional[str] = None
    especializaciones: Optional[List[str]] = None
    grupo_etario: Optional[List[str]] = None
    es_emergencia: bool = False
    es_gratuito: bool = False
    
    # Filtros duros para reranking
    genero_especialista: Optional[str] = None  # "Masculino", "Femenino", "Mixto"
    delegacion_exacta: bool = False  # True = delegación debe coincidir exactamente
    requiere_sabado: bool = False  # True = debe atender sábados
    costo_maximo_absoluto: Optional[float] = None  # Límite absoluto de costo
    metodo_pago_requerido: Optional[str] = None  # "Tarjeta", "Efectivo", "Seguros", etc.


class MentalHealthRetrieval:
    """
    Sistema de retrieval para encontrar especialistas de salud mental
    usando búsqueda semántica y filtros específicos
    """
    
    def __init__(self,
                 json_path: str,
                 openai_model: str = 'text-embedding-3-small',
                 index_path: str = 'faiss_recursos/recursos_index.bin',
                 metadata_path: str = 'faiss_recursos/recursos_metadata.pkl',
                 force_rebuild: bool = False):
        """
        Inicializa el sistema de retrieval usando OpenAI embeddings y FAISS
        
        Args:
            json_path: Ruta al archivo JSON con recursos (especialistas y servicios)
            openai_model: Modelo de OpenAI embeddings (default: text-embedding-3-small)
            index_path: Ruta donde guardar/cargar índice FAISS
            metadata_path: Ruta donde guardar/cargar metadatos
            force_rebuild: Si True, reconstruye embeddings aunque exista cache
        """
        # Cargar datos (ahora es una base de datos unificada)
        with open(json_path, 'r', encoding='utf-8') as f:
            self.recursos = json.load(f)
        
        # Mantener compatibilidad con código existente
        self.especialistas = self.recursos
        
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
            print(f"Cargando indice FAISS desde {index_path}")
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                cached_data = pickle.load(f)
                self.especialistas = cached_data['especialistas']
            print(f"Indice cargado con {self.index.ntotal} vectores")
        else:
            print(f"Usando OpenAI embeddings: {self.openai_model}")
            print("Generando embeddings para especialistas")
            embeddings = self._generate_embeddings_openai()
            
            # Convertir a float32 para FAISS
            embeddings = embeddings.astype('float32')
            
            # Crear índice FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalizar vectores para cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            # Guardar índice y metadatos
            print(f"Guardando indice FAISS en {self.index_path}")
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({'especialistas': self.especialistas}, f)
            print("Indice guardado")
        
        print(f"Sistema listo con {len(self.especialistas)} especialistas")
    
    def _create_specialist_text(self, recurso: Dict[str, Any]) -> str:
        """
        Crea un texto descriptivo del recurso (especialista o servicio) para embeddings
        Incluye toda la información relevante para búsqueda semántica
        """
        parts = [
            recurso.get('nombre', ''),
            recurso.get('tipo_profesional', ''),
            recurso.get('modalidad', ''),
            recurso.get('institucion', ''),
            recurso.get('descripcion', ''),
            recurso.get('tipo_recurso', ''),  # 'especialista' o 'servicio'
        ]
        
        # Especialidades/especializaciones (muy importante)
        if 'especializaciones' in recurso:
            parts.append(' '.join(recurso['especializaciones']))
        
        # Servicios ofrecidos (para servicios públicos)
        if 'servicios_ofrecidos' in recurso:
            parts.append(' '.join(recurso['servicios_ofrecidos']))
        
        # Tipo de servicio (para servicios)
        if 'tipo_servicio' in recurso and recurso['tipo_servicio']:
            parts.append(recurso['tipo_servicio'])
        
        # Ubicación
        if 'ubicacion' in recurso:
            ubi = recurso['ubicacion']
            parts.extend([
                ubi.get('colonia', ''),
                ubi.get('delegacion', ''),
            ])
        
        # Grupos etarios
        if 'grupo_etario' in recurso:
            parts.append(' '.join(recurso['grupo_etario']))
        
        # Tags de matching
        if 'tags_match' in recurso:
            parts.append(recurso['tags_match'])
        
        # Descripción del costo para contexto
        if 'costo' in recurso:
            if isinstance(recurso['costo'], dict):
                if 'descripcion' in recurso['costo']:
                    parts.append(recurso['costo']['descripcion'])
                if recurso['costo'].get('es_gratuito'):
                    parts.append('gratuito gratis sin costo')
        
        # Emergencia
        if recurso.get('es_emergencia'):
            parts.append('emergencia crisis urgente inmediato 24/7')
        
        return ' '.join([p for p in parts if p])
    
    def _generate_embeddings_openai(self) -> np.ndarray:
        """Genera embeddings usando la OpenAI Embeddings API en batch."""
        texts = [self._create_specialist_text(rec) for rec in self.recursos]
        all_embeddings = []
        batch_size = 50
        
        print(f"Generando embeddings para {len(texts)} recursos en batches de {batch_size}")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for attempt in range(3):
                try:
                    resp = self.client.embeddings.create(model=self.openai_model, input=batch)
                    batch_emb = [d.embedding for d in resp.data]
                    all_embeddings.extend(batch_emb)
                    print(f"Batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} completado")
                    time.sleep(0.1)
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"Error en batch {i//batch_size + 1}: {e}")
                        raise
                    print(f"Reintento {attempt + 1}/3")
                    time.sleep(1 + attempt)

        return np.array(all_embeddings)
    
    def _apply_filters(self, recurso: Dict[str, Any], filters: QueryFilters) -> bool:
        """
        Aplica filtros específicos al recurso (especialista o servicio)
        Retorna True si el recurso cumple con los filtros
        """
        # Filtro de costo máximo (funciona para ambos tipos)
        if filters.max_cost is not None:
            costo_info = recurso.get('costo', {})
            if isinstance(costo_info, dict):
                costo_promedio = costo_info.get('promedio', 0)
                # También revisar cantidad_min para compatibilidad con datos antiguos
                costo_min = costo_info.get('cantidad_min', costo_promedio)
                costo_actual = costo_min if costo_min > 0 else costo_promedio
                if costo_actual > filters.max_cost:
                    return False
        
        # Filtro de rating mínimo
        if filters.min_rating is not None:
            rating = recurso.get('rating', 0)
            if rating < filters.min_rating:
                return False
        
        # Filtro de modalidad
        if filters.modalidad:
            modalidad = recurso.get('modalidad', '')
            # Verificar si alguna modalidad del filtro está en la modalidad del recurso
            if not any(mod.lower() in modalidad.lower() for mod in filters.modalidad):
                return False
        
        # Filtro de tipo profesional
        if filters.tipo_profesional:
            tipo = recurso.get('tipo_profesional', '')
            if not any(tp.lower() in tipo.lower() for tp in filters.tipo_profesional):
                return False
        
        # Filtro de delegación
        if filters.delegacion:
            delegacion = recurso.get('ubicacion', {}).get('delegacion', '')
            if filters.delegacion.lower() not in delegacion.lower():
                return False
        
        # Filtro de especializaciones
        if filters.especializaciones:
            specs = recurso.get('especializaciones', [])
            specs_lower = [s.lower() for s in specs]
            # Al menos una especialización debe coincidir
            if not any(f.lower() in ' '.join(specs_lower) for f in filters.especializaciones):
                return False
        
        # Filtro de grupo etario
        if filters.grupo_etario:
            grupos = recurso.get('grupo_etario', [])
            if not any(ge in grupos for ge in filters.grupo_etario):
                return False
        
        # Filtro de emergencia
        if filters.es_emergencia:
            # Revisar si es_emergencia está marcado o buscar en tipo/tags
            if recurso.get('es_emergencia', False):
                return True
            tipo = recurso.get('tipo_profesional', '').lower()
            tags = recurso.get('tags_match', '').lower()
            if 'emergencia' not in tipo and 'emergencia' not in tags and 'crisis' not in tags:
                return False
        
        # Filtro de gratuito/bajo costo
        if filters.es_gratuito:
            costo_info = recurso.get('costo', {})
            if isinstance(costo_info, dict):
                # Revisar flag es_gratuito o costo promedio
                if costo_info.get('es_gratuito', False):
                    return True
                costo_promedio = costo_info.get('promedio', 0)
                costo_min = costo_info.get('cantidad_min', costo_promedio)
                costo_actual = costo_min if costo_min > 0 else costo_promedio
                if costo_actual > 500:  # Consideramos gratuito o muy bajo costo
                    return False
        
        return True
    
    def _apply_hard_filters(self, recurso: Dict[str, Any], filters: QueryFilters) -> tuple[bool, str]:
        """
        Aplica filtros duros (reglas estrictas de negocio) para reranking.
        Retorna (pass, reason) donde pass=True si cumple todos los filtros duros.
        """
        # Filtros duros de género (si se especifica) - solo para especialistas
        if hasattr(filters, 'genero_especialista') and filters.genero_especialista:
            genero = recurso.get('genero_especialista')
            # Si es un servicio sin género o el valor es None, pasa el filtro
            if genero:
                genero_lower = genero.lower()
                if filters.genero_especialista.lower() not in genero_lower and genero_lower != 'mixto':
                    return False, f"Género no coincide (buscado: {filters.genero_especialista})"
        
        # Filtros duros de ubicación (delegación exacta si se requiere)
        if hasattr(filters, 'delegacion_exacta') and filters.delegacion_exacta:
            delegacion = recurso.get('ubicacion', {}).get('delegacion', '')
            if delegacion and filters.delegacion:
                if filters.delegacion.lower() != delegacion.lower():
                    return False, f"Delegación no coincide exactamente"
        
        # Filtros duros de disponibilidad (si requiere horario específico)
        if hasattr(filters, 'requiere_sabado') and filters.requiere_sabado:
            # Revisar flag tiene_sabado si existe
            if recurso.get('tiene_sabado', False):
                pass  # Tiene sábado, continúa
            else:
                disponibilidad = recurso.get('disponibilidad', '').lower()
                if 'sábado' not in disponibilidad and 'sabado' not in disponibilidad and '24' not in disponibilidad:
                    return False, "No atiende sábados"
        
        # Filtros duros de costo (costo máximo absoluto)
        if hasattr(filters, 'costo_maximo_absoluto') and filters.costo_maximo_absoluto:
            costo_info = recurso.get('costo', {})
            if isinstance(costo_info, dict):
                costo_promedio = costo_info.get('promedio', 0)
                costo_min = costo_info.get('cantidad_min', costo_promedio)
                costo_actual = costo_min if costo_min > 0 else costo_promedio
                if costo_actual > filters.costo_maximo_absoluto:
                    return False, f"Costo excede límite absoluto (${costo_actual} > ${filters.costo_maximo_absoluto})"
        
        # Filtros duros de métodos de pago
        if hasattr(filters, 'metodo_pago_requerido') and filters.metodo_pago_requerido:
            metodos = recurso.get('metodos_pago', [])
            metodos_lower = [m.lower() for m in metodos]
            if filters.metodo_pago_requerido.lower() not in metodos_lower:
                return False, f"No acepta {filters.metodo_pago_requerido}"
        
        return True, "OK"
    
    def _calculate_score(self, 
                        recurso: Dict[str, Any], 
                        similarity: float,
                        filters: QueryFilters) -> float:
        """
        Calcula un score híbrido considerando:
        - Similitud semántica (70%)
        - Rating (15%)
        - Costo (10% - menor costo, mejor score)
        - Disponibilidad (5%)
        """
        # Similitud semántica (peso mayor)
        semantic_score = similarity * 0.70
        
        # Rating normalizado (0-5 -> 0-1)
        rating = recurso.get('rating', 0)
        rating_score = (rating / 5.0) * 0.15
        
        # Costo normalizado (inverso: menor costo = mejor score)
        costo_info = recurso.get('costo', {})
        if isinstance(costo_info, dict):
            costo_promedio = costo_info.get('promedio', 0)
            costo_min = costo_info.get('cantidad_min', costo_promedio)
            costo_actual = costo_min if costo_min > 0 else costo_promedio
        else:
            costo_actual = 1500  # Default si no hay info
        
        if costo_actual == 0 or costo_info.get('es_gratuito', False):
            cost_score = 0.10  # Máximo para gratuito
        else:
            # Normalizar: 0-2000 MXN invertido
            cost_score = (1 - min(costo_actual / 2000, 1)) * 0.10
        
        # Disponibilidad (boost si tiene múltiples modalidades u horario amplio)
        availability_score = 0
        modalidad = recurso.get('modalidad', '')
        if 'online' in modalidad.lower() and 'presencial' in modalidad.lower():
            availability_score += 0.03
        disponibilidad = recurso.get('disponibilidad', '').lower()
        if '24' in disponibilidad or 'sábado' in disponibilidad or 'sabado' in disponibilidad:
            availability_score += 0.02
        
        # Boost para emergencias si aplica
        if filters and filters.es_emergencia and recurso.get('es_emergencia', False):
            availability_score += 0.05
        
        # Score total
        total_score = semantic_score + rating_score + cost_score + availability_score
        
        return total_score
    
    def search(self, 
               query: str, 
               filters: Optional[QueryFilters] = None,
               top_k: int = 5,
               apply_reranking: bool = True) -> List[Dict[str, Any]]:
        """
        Busca los mejores especialistas según la query y filtros
        
        Args:
            query: Descripción de lo que busca el usuario
            filters: Filtros opcionales
            top_k: Número de resultados a devolver
            apply_reranking: Si True, aplica reranking con filtros duros a candidatos
            
        Returns:
            Lista de especialistas ordenados por relevancia con scores
        """
        if filters is None:
            filters = QueryFilters()
        
        # Generar embedding de la query usando OpenAI
        resp = self.client.embeddings.create(model=self.openai_model, input=[query])
        query_embedding = np.array(resp.data[0].embedding, dtype='float32').reshape(1, -1)
        
        # Normalizar para cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Buscar en FAISS (buscar más candidatos de los necesarios para reranking)
        k_search = min(top_k * 3, self.index.ntotal)
        similarities, indices = self.index.search(query_embedding, k_search)
        
        similarities = similarities[0]  # Aplanar
        indices = indices[0]
        
        # PASO 1: Filtrar con filtros suaves y calcular scores
        candidates = []
        for idx, similarity_score in zip(indices, similarities):
            specialist = self.especialistas[idx]
            
            # Aplicar filtros suaves
            if not self._apply_filters(specialist, filters):
                continue
            
            # Calcular score híbrido
            score = self._calculate_score(specialist, similarity_score, filters)
            
            # Agregar a candidatos
            result = specialist.copy()
            result['relevance_score'] = float(score)
            result['semantic_similarity'] = float(similarity_score)
            candidates.append(result)
        
        # Ordenar candidatos por score
        candidates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # PASO 2: Reranking con filtros duros (reglas estrictas)
        if apply_reranking and len(candidates) > 0:
            # Tomar top candidatos (más que top_k para tener margen)
            rerank_pool_size = min(top_k * 3, len(candidates))
            rerank_pool = candidates[:rerank_pool_size]
            
            # Aplicar filtros duros
            passed = []
            failed = []
            for candidate in rerank_pool:
                passes, reason = self._apply_hard_filters(candidate, filters)
                if passes:
                    passed.append(candidate)
                else:
                    candidate['filter_fail_reason'] = reason
                    failed.append(candidate)
            
            # Si quedan suficientes que pasaron filtros duros, usar esos
            if len(passed) >= top_k:
                return passed[:top_k]
            # Si no hay suficientes, complementar con los que fallaron
            else:
                return passed + failed[:top_k - len(passed)]
        
        # Si no se aplica reranking, retornar top k directamente
        return candidates[:top_k]
    
    def format_result(self, specialist: Dict[str, Any]) -> str:
        """
        Formatea un resultado para mostrar al usuario de forma clara
        Ideal para lectura por voz en la app móvil
        """
        nombre = specialist.get('nombre', 'N/A')
        tipo = specialist.get('tipo_profesional', 'N/A')
        modalidad = specialist.get('modalidad', 'N/A')
        
        # Costo
        costo_desc = specialist.get('costo', {}).get('descripcion', 'N/A')
        
        # Ubicación
        ubi = specialist.get('ubicacion', {})
        ubicacion = f"{ubi.get('colonia', '')}, {ubi.get('delegacion', '')}"
        
        # Especialidades principales (primeras 3)
        specs = specialist.get('especializaciones', [])[:3]
        specs_text = ', '.join(specs) if specs else 'N/A'
        
        # Rating y reseñas
        rating = specialist.get('rating', 0)
        resenas = specialist.get('resenas', 0)
        
        # Contacto
        contacto = specialist.get('contacto', {})
        telefono = contacto.get('telefono', 'N/A')
        
        # Scores (si están disponibles)
        relevance = specialist.get('relevance_score', 0)
        
        output = f"""
            ╔════════════════════════════════════════════════════════
            ║ {nombre}
            ╠════════════════════════════════════════════════════════
            ║ Tipo: {tipo}
            ║ Modalidad: {modalidad}
            ║ Ubicacion: {ubicacion}
            ║ Costo: {costo_desc}
            ║ Rating: {rating}/5.0 ({resenas} resenas)
            ║ Especialidades: {specs_text}
            ║ Contacto: {telefono}
            ║ Score de Relevancia: {relevance:.3f}
            ╚════════════════════════════════════════════════════════
            """
        return output


if __name__ == "__main__":
    # Sistema listo para ser importado y usado por el API
    pass
