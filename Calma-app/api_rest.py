"""
API REST para el Sistema de Retrieval de Especialistas
Diseñado para integración con aplicación móvil

Uso:
    python api_rest.py

Endpoints:
    POST /search - Buscar especialistas
    GET /health - Health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG.retrieval_system import MentalHealthRetrieval, QueryFilters
from RAG.knowledge_rag import MentalHealthKnowledgeRAG
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir CORS para llamadas desde móvil

# Variables globales para sistemas (se cargan al iniciar para respuestas rápidas)
retrieval_system = None
knowledge_system = None

# Pre-cargar sistemas al iniciar (evita lazy loading en primera request)
def init_systems():
    """Inicializa los sistemas al arrancar Gunicorn (solo una vez)"""
    global retrieval_system, knowledge_system
    if retrieval_system is None:
        logger.info("Pre-cargando sistema de retrieval...")
        retrieval_system = MentalHealthRetrieval('datos/recursos_salud_mental_cdmx.json')
        logger.info("✓ Sistema RecSys listo")
    if knowledge_system is None:
        logger.info("Pre-cargando sistema de conocimiento...")
        knowledge_system = MentalHealthKnowledgeRAG('datos/base_conocimiento_rag_pasos_inmediatos.json')
        logger.info("✓ Sistema RAG listo")

# Cargar en el primer request usando before_first_request
@app.before_request
def ensure_systems_loaded():
    """Asegura que los sistemas estén cargados antes de cualquier request"""
    logger.info(f"Incoming request: {request.method} {request.path}")
    if retrieval_system is None or knowledge_system is None:
        logger.warning(" Sistemas no cargados, inicializando...")
        init_systems()

@app.after_request
def log_response(response):
    """Log de todas las respuestas"""
    logger.info(f"Outgoing response: {request.method} {request.path} - Status: {response.status_code}")
    return response

# Palabras clave de crisis y alto riesgo
CRISIS_KEYWORDS = [
    'suicid', 'suicidio', 'suicidarme', 'matarme', 'quitarme la vida',
    'morir', 'muerte', 'acabar con todo', 'no quiero vivir',
    'mejor muerto', 'quiero desaparecer', 'hacerme daño',
    'cortarme', 'autolesion', 'pastillas para morir',
    'plan para suicidarme', 'quiero que acabe', 'ya no puedo más'
]

HIGH_RISK_KEYWORDS = [
    'pánico', 'panico', 'crisis', 'desesperado', 'desesperada',
    'muy mal', 'horrible', 'insoportable', 'no aguanto',
    'colapso', 'emergencia', 'urgente', 'ayuda inmediata'
]

def detectar_nivel_crisis(texto: str) -> tuple[str, bool]:
    """
    Detecta nivel de crisis en el texto del usuario
    
    Returns:
        tuple: (nivel, requiere_emergencia)
        - nivel: 'CRITICO', 'ALTO', 'MODERADO', 'NORMAL'
        - requiere_emergencia: bool
    """
    texto_lower = texto.lower()
    
    # Detectar crisis crítica (suicidio/autolesión)
    for keyword in CRISIS_KEYWORDS:
        if keyword in texto_lower:
            logger.critical(f"CRISIS DETECTADA: palabra clave '{keyword}' en texto")
            return 'CRITICO', True
    
    # Detectar alto riesgo
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in texto_lower:
            logger.warning(f"ALTO RIESGO: palabra clave '{keyword}' en texto")
            return 'ALTO', True
    
    return 'NORMAL', False

def generar_respuesta_empatica(sintoma: str, nivel_crisis: str, num_resultados: int, 
                               tiene_resultados: bool, genero: str = '', 
                               ubicacion: str = '', primer_resultado: dict = None) -> str:
    """
    Genera respuesta de voz empática según el nivel de crisis
    
    Args:
        sintoma: Síntoma o problema del usuario
        nivel_crisis: 'CRITICO', 'ALTO', 'MODERADO', 'NORMAL'
        num_resultados: Cantidad de resultados encontrados
        tiene_resultados: Si hay resultados disponibles
        genero: Género preferido del especialista
        ubicacion: Ubicación solicitada
        primer_resultado: Primer especialista encontrado
    
    Returns:
        str: Respuesta de voz empática y apropiada
    """
    if nivel_crisis == 'CRITICO':
        return (
            f"Escucho que estás pasando por un momento muy difícil. "
            f"Tu seguridad es lo más importante. "
            f"Por favor, llama INMEDIATAMENTE a la Línea de la Vida: 800-911-2000, "
            f"o al 911 si necesitas ayuda urgente. Están disponibles 24/7 y es completamente gratuito. "
            f"También encontré {num_resultados} especialista{'s' if num_resultados > 1 else ''} que puede{'n' if num_resultados > 1 else ''} apoyarte, "
            f"pero por favor, contacta primero a los servicios de emergencia."
        )
    
    if nivel_crisis == 'ALTO':
        respuesta = f"Entiendo que estás pasando por un momento muy difícil con {sintoma}. "
        if not tiene_resultados:
            respuesta += "Aunque no encontré especialistas con los criterios exactos, "
            respuesta += "es importante que busques ayuda. ¿Quieres que busque con otros criterios? "
            respuesta += "Si sientes que es una emergencia, puedes llamar al 800-911-2000."
        else:
            respuesta += f"Encontré {num_resultados} especialista{'s' if num_resultados > 1 else ''} "
            if genero:
                respuesta += f"{genero}{'es' if num_resultados > 1 else ''} "
            respuesta += f"que puede{'n' if num_resultados > 1 else ''} ayudarte. "
            
            if primer_resultado:
                nombre = primer_resultado.get('nombre', 'un especialista')
                modalidad = primer_resultado.get('modalidad', 'Presencial')
                delegacion = primer_resultado.get('ubicacion', {}).get('delegacion', '')
                costo = primer_resultado.get('costo', 'Información de costo disponible')
                
                respuesta += f"Te recomiendo a {nombre}, trabaja {modalidad}"
                if ubicacion:
                    respuesta += f" en {delegacion}"
                respuesta += f". {costo}. "
                
                if num_resultados > 1:
                    respuesta += f"También tengo {num_resultados - 1} opcione{'s' if num_resultados > 2 else ''} más."
            
            respuesta += " Recuerda que no estás solo, hay personas que quieren ayudarte."
        return respuesta
    
    # NORMAL - respuesta empática pero menos intensa
    if not tiene_resultados:
        respuesta = f"Entiendo que estás buscando ayuda con {sintoma}. "
        respuesta += "Lamentablemente no encontré especialistas"
        if genero:
            respuesta += f" {genero}es"
        if ubicacion:
            respuesta += f" en {ubicacion}"
        respuesta += ". ¿Te gustaría que busque con otros criterios o en otra zona?"
    else:
        respuesta = f"Gracias por confiar en mí. Encontré {num_resultados} especialista{'s' if num_resultados > 1 else ''} "
        if genero:
            respuesta += f"{genero}{'es' if num_resultados > 1 else ''} "
        respuesta += f"que puede{'n' if num_resultados > 1 else ''} ayudarte con {sintoma}. "
        
        if primer_resultado:
            nombre = primer_resultado.get('nombre', 'un especialista')
            modalidad = primer_resultado.get('modalidad', 'Presencial')
            delegacion = primer_resultado.get('ubicacion', {}).get('delegacion', '')
            costo = primer_resultado.get('costo', 'Información disponible')
            
            respuesta += f"Mi mejor recomendación es {nombre}, trabaja {modalidad}"
            if ubicacion:
                respuesta += f" en {delegacion}"
            respuesta += f". {costo}. "
            
            if num_resultados > 1:
                respuesta += f"También tengo {num_resultados - 1} opcione{'s' if num_resultados > 2 else ''} más que te pueden interesar."
    
    return respuesta

def get_retrieval_system():
    """Retorna el sistema de retrieval (ya pre-cargado)"""
    global retrieval_system
    if retrieval_system is None:
        init_systems()
    return retrieval_system

def get_knowledge_system():
    """Retorna el sistema de conocimiento (ya pre-cargado)"""
    global knowledge_system
    if knowledge_system is None:
        init_systems()
    return knowledge_system


def parse_filters(request_data: Dict[str, Any]) -> QueryFilters:
    """
    Parsea los filtros desde el request JSON
    """
    filters = QueryFilters()
    
    if 'max_cost' in request_data:
        filters.max_cost = float(request_data['max_cost'])
    
    if 'min_rating' in request_data:
        filters.min_rating = float(request_data['min_rating'])
    
    if 'modalidad' in request_data:
        filters.modalidad = request_data['modalidad']
    
    if 'tipo_profesional' in request_data:
        filters.tipo_profesional = request_data['tipo_profesional']
    
    if 'delegacion' in request_data:
        filters.delegacion = request_data['delegacion']
    
    if 'especializaciones' in request_data:
        filters.especializaciones = request_data['especializaciones']
    
    if 'grupo_etario' in request_data:
        filters.grupo_etario = request_data['grupo_etario']
    
    if 'es_emergencia' in request_data:
        filters.es_emergencia = bool(request_data['es_emergencia'])
    
    if 'es_gratuito' in request_data:
        filters.es_gratuito = bool(request_data['es_gratuito'])
    
    return filters


def format_for_elevenlabs(results: list) -> list:
    """
    Formatea resultados MINIMOS para ElevenLabs (respuesta rapida)
    Solo incluye campos esenciales para la conversacion
    """
    elevenlabs_results = []
    
    for result in results:
        elevenlabs_results.append({
            'nombre': result.get('nombre'),
            'tipo': result.get('tipo_profesional'),
            'ubicacion': result.get('ubicacion', {}).get('delegacion', 'CDMX'),
            'costo': result.get('costo', {}).get('descripcion', 'Consultar'),
            'telefono': result.get('contacto', {}).get('telefono', ''),
            'especializaciones': result.get('especializaciones', [])[:3]  # Max 3
        })
    
    return elevenlabs_results


def format_for_mobile(results: list) -> list:
    """
    Formatea resultados para consumo desde app móvil
    Simplifica y estructura la información
    """
    mobile_results = []
    
    for result in results:
        mobile_result = {
            'id': result.get('id'),
            'nombre': result.get('nombre'),
            'tipo_profesional': result.get('tipo_profesional'),
            'modalidad': result.get('modalidad'),
            'ubicacion': {
                'colonia': result.get('ubicacion', {}).get('colonia'),
                'delegacion': result.get('ubicacion', {}).get('delegacion'),
                'latitud': result.get('ubicacion', {}).get('latitud'),
                'longitud': result.get('ubicacion', {}).get('longitud'),
            },
            'costo': result.get('costo', {}).get('descripcion'),
            'costo_min': result.get('costo', {}).get('cantidad_min'),
            'rating': result.get('rating'),
            'resenas': result.get('resenas'),
            'especializaciones': result.get('especializaciones', []),
            'grupo_etario': result.get('grupo_etario', []),
            'contacto': {
                'telefono': result.get('contacto', {}).get('telefono'),
                'email': result.get('contacto', {}).get('email'),
                'website': result.get('contacto', {}).get('website'),
            },
            'disponibilidad': result.get('disponibilidad'),
            'metodos_pago': result.get('metodos_pago', []),
            'scores': {
                'relevance': round(result.get('relevance_score', 0), 3),
                'similarity': round(result.get('semantic_similarity', 0), 3)
            }
        }
        mobile_results.append(mobile_result)
    
    return mobile_results


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Mental Health Retrieval API',
        'version': '1.0.0',
        'systems': {
            'retrieval_loaded': retrieval_system is not None,
            'knowledge_loaded': knowledge_system is not None
        }
    })


@app.route('/debug', methods=['GET'])
def debug_info():
    """
    Endpoint de debug para verificar el estado del sistema
    """
    import sys
    return jsonify({
        'status': 'debug',
        'systems': {
            'retrieval_loaded': retrieval_system is not None,
            'knowledge_loaded': knowledge_system is not None,
            'retrieval_specialists_count': len(retrieval_system.especialistas) if retrieval_system else 0,
            'knowledge_articles_count': len(knowledge_system.articles) if knowledge_system else 0
        },
        'python_version': sys.version,
        'endpoints': [
            '/health',
            '/debug',
            '/search',
            '/emergency',
            '/buscar_especialista',
            '/consultar_guia_medica'
        ]
    })


@app.route('/search', methods=['POST'])
def search_specialists():
    """
    Endpoint principal para buscar especialistas
    
    Body (JSON):
    {
        "query": "Necesito ayuda con ansiedad",
        "top_k": 5,
        "filters": {
            "max_cost": 800,
            "min_rating": 4.5,
            "modalidad": ["Online"],
            "es_emergencia": false
        }
    }
    
    Response:
    {
        "success": true,
        "query": "Necesito ayuda con ansiedad",
        "total_results": 5,
        "results": [...]
    }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo "query" es requerido'
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Validar top_k
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({
                'success': False,
                'error': 'top_k debe ser un entero entre 1 y 20'
            }), 400
        
        # Parsear filtros
        filters = None
        if 'filters' in data:
            filters = parse_filters(data['filters'])
        
        logger.info(f"Búsqueda: '{query}' | Top K: {top_k} | Filtros: {filters}")
        
        # Realizar búsqueda
        results = get_retrieval_system().search(query, filters=filters, top_k=top_k)
        
        # Formatear para móvil
        mobile_results = format_for_mobile(results)
        
        # Respuesta
        response = {
            'success': True,
            'query': query,
            'total_results': len(mobile_results),
            'results': mobile_results
        }
        
        logger.info(f"Retornando {len(mobile_results)} resultados")
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/emergency', methods=['POST'])
def emergency_search():
    """
    Endpoint especial para casos de emergencia
    Automáticamente aplica filtros para crisis
    
    Body (JSON):
    {
        "query": "Pensamientos suicidas",
        "max_cost": 500  // opcional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo "query" es requerido'
            }), 400
        
        query = data['query']
        max_cost = data.get('max_cost', 1000)
        
        # Filtros automáticos para emergencia
        filters = QueryFilters(
            es_emergencia=True,
            max_cost=max_cost
        )
        
        logger.warning(f"BUSQUEDA DE EMERGENCIA: '{query}'")
        
        # Buscar solo top 3 más relevantes en emergencia
        results = get_retrieval_system().search(query, filters=filters, top_k=3)
        mobile_results = format_for_mobile(results)
        
        response = {
            'success': True,
            'emergency': True,
            'query': query,
            'total_results': len(mobile_results),
            'results': mobile_results,
            'message': 'Si estás en crisis, contacta inmediatamente: Línea de la Vida 800-911-2000'
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en búsqueda de emergencia: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/buscar_especialista', methods=['POST'])
def buscar_especialista():
    """
    Endpoint para ElevenLabs Tool: Buscar especialistas/doctores
    Compatible con los 4 parámetros configurados en ElevenLabs.
    
    Body (JSON):
    {
        "sintoma": "ansiedad",           // REQUERIDO - Síntoma o problema principal
        "genero": "mujer",               // OPCIONAL - Género preferido del especialista
        "presupuesto": "barato",         // OPCIONAL - Restricción económica
        "ubicacion": "Coyoacán"          // OPCIONAL - Zona o delegación
    }
    
    Response:
    {
        "success": true,
        "respuesta_voz": "Encontré 3 especialistas...",
        "resultados": [...]
    }
    """
    try:
        data = request.get_json()
        
        # Validar parámetro requerido
        if not data or 'sintoma' not in data:
            return jsonify({
                'success': False,
                'error': 'El parámetro "sintoma" es requerido',
                'respuesta_voz': 'Lo siento, necesito que me digas qué síntoma o problema tienes.'
            }), 400
        
        # Extraer parámetros
        sintoma = data['sintoma']
        genero = data.get('genero', '').lower()  # hombre, mujer, etc.
        presupuesto = data.get('presupuesto', '')
        ubicacion = data.get('ubicacion', '')
        
        # 🚨 DETECCIÓN DE CRISIS
        nivel_crisis, requiere_emergencia = detectar_nivel_crisis(sintoma)
        
        if requiere_emergencia:
            logger.critical(f"CRISIS DETECTADA - Usuario: '{sintoma}' - Nivel: {nivel_crisis}")
            # Activar endpoint de emergencia automáticamente
            if nivel_crisis == 'CRITICO':
                # Redirigir a protocolo de emergencia
                filters_emergencia = QueryFilters(
                    es_emergencia=True,
                    max_cost=2000  # Menos restrictivo en crisis
                )
                results = get_retrieval_system().search(
                    f"crisis psicológica {sintoma}", 
                    filters=filters_emergencia, 
                    top_k=3
                )
                mobile_results = format_for_mobile(results)
                
                respuesta_voz = generar_respuesta_empatica(
                    sintoma=sintoma,
                    nivel_crisis=nivel_crisis,
                    num_resultados=len(mobile_results),
                    tiene_resultados=len(mobile_results) > 0,
                    genero=genero,
                    ubicacion=ubicacion,
                    primer_resultado=mobile_results[0] if mobile_results else None
                )
                
                return jsonify({
                    'success': True,
                    'alerta_crisis': True,
                    'nivel_urgencia': nivel_crisis,
                    'respuesta_voz': respuesta_voz,
                    'numeros_emergencia': {
                        'mexico': '800-911-2000 (Línea de la Vida - 24/7 GRATUITO)',
                        'emergencia_general': '911',
                        'mensaje': 'Por favor contacta inmediatamente si estás en peligro'
                    },
                    'parametros': {
                        'sintoma': sintoma,
                        'genero': genero or 'no especificado',
                        'presupuesto': presupuesto or 'no especificado',
                        'ubicacion': ubicacion or 'no especificado'
                    },
                    'total_resultados': len(mobile_results),
                    'resultados': mobile_results
                }), 200
        
        # Construir query natural para el RecSys
        query_parts = [f"Necesito ayuda con {sintoma}"]
        
        # Detectar si es una búsqueda de servicio digital/app (meditación, relajación, etc.)
        es_busqueda_digital = any(word in sintoma.lower() for word in [
            'meditación', 'meditacion', 'mindfulness', 'app', 'aplicación', 
            'aplicacion', 'herramienta', 'relajación', 'relajacion', 'yoga', 
            'respiración', 'respiracion', 'ejercicio', 'autoayuda'
        ])
        
        if ubicacion and not es_busqueda_digital:
            query_parts.append(f"cerca de {ubicacion}")
        if genero:
            query_parts.append(f"especialista {genero}")
        query = " ".join(query_parts)
        
        # Configurar filtros según parámetros
        filters = QueryFilters()
        
        # Filtro de presupuesto
        if presupuesto:
            presupuesto_lower = presupuesto.lower()
            if any(word in presupuesto_lower for word in ['barato', 'económico', 'gratuito', 'gratis', 'sin dinero', 'estudiante', 'barata']):
                filters.max_cost = 600
                filters.es_gratuito = True
            elif any(word in presupuesto_lower for word in ['medio', 'moderado', 'accesible', 'razonable']):
                filters.max_cost = 1200
            elif any(word in presupuesto_lower for word in ['caro', 'premium', 'privado']):
                filters.max_cost = 3000
            # Si no especifica límite, dejamos sin restricción
        
        # Filtro de ubicación (NO aplicar para búsquedas digitales)
        if ubicacion and not es_busqueda_digital:
            filters.delegacion = ubicacion
        
        # Filtro de género (usar el campo correcto del sistema)
        if genero:
            # Mapear los valores comunes a los esperados por el sistema
            genero_map = {
                'hombre': 'Masculino',
                'masculino': 'Masculino',
                'mujer': 'Femenino',
                'femenino': 'Femenino',
                'femenina': 'Femenino',
                'cualquiera': 'Mixto',
                'indistinto': 'Mixto'
            }
            genero_normalizado = genero_map.get(genero, genero.capitalize())
            filters.genero_especialista = genero_normalizado
        
        # Log de búsqueda
        logger.info(f"Busqueda especialista: sintoma='{sintoma}', genero='{genero}', presupuesto='{presupuesto}', ubicacion='{ubicacion}'")
        logger.info(f"   Query construida: '{query}'")
        logger.info(f"   Es búsqueda digital: {es_busqueda_digital}")
        logger.info(f"   Filtros aplicados: max_cost={filters.max_cost}, delegacion={filters.delegacion}, genero={filters.genero_especialista}")
        
        # Buscar especialistas (top 10 para tener más opciones disponibles)
        offset = data.get('offset', 0)  # Parámetro de paginación
        top_k = data.get('top_k', 10)   # Aumentado a 10 por defecto
        
        results = get_retrieval_system().search(query, filters=filters, top_k=top_k)
        
        logger.info(f"Encontrados {len(results)} resultados totales")
        
        # Aplicar offset para paginación
        results_paginados = results[offset:offset+3]  # Mostrar 3 por página
        total_disponibles = len(results)
        hay_mas = (offset + 3) < total_disponibles
        
        logger.info(f"   Mostrando resultados {offset+1} a {offset+len(results_paginados)} de {total_disponibles}")
        
        # Formatear para móvil (completo) y para ElevenLabs (ligero)
        mobile_results = format_for_mobile(results_paginados)
        elevenlabs_results = format_for_elevenlabs(results_paginados)
        
        # Generar respuesta empática usando la función
        respuesta_voz = generar_respuesta_empatica(
            sintoma=sintoma,
            nivel_crisis=nivel_crisis,
            num_resultados=len(mobile_results),
            tiene_resultados=len(mobile_results) > 0,
            genero=genero,
            ubicacion=ubicacion,
            primer_resultado=mobile_results[0] if mobile_results else None
        )
        
        # Agregar información sobre resultados adicionales
        if hay_mas:
            resultados_restantes = total_disponibles - (offset + len(results_paginados))
            respuesta_voz += f" Tengo {resultados_restantes} opciones mas. Quieres conocerlas?"
        
        # Respuesta SIMPLIFICADA para ElevenLabs (evitar errores de parsing)
        response = {
            'respuesta_voz': respuesta_voz,
            'sintoma': sintoma,
            'total_resultados': len(elevenlabs_results),
            'resultados': elevenlabs_results
        }
        
        # Solo agregar campos extras si es crisis
        if nivel_crisis in ['CRITICO', 'ALTO']:
            response['emergencia'] = '800-911-2000'
        
        logger.info(f"Retornando {len(mobile_results)} resultados para buscar_especialista")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en buscar_especialista: {str(e)}")
        logger.exception(e)  # Esto imprime el stack trace completo
        return jsonify({
            'success': False,
            'error': str(e),
            'respuesta_voz': 'Lo siento, tuve un problema técnico al buscar especialistas. ¿Puedes intentarlo de nuevo?'
        }), 500


@app.route('/consultar_guia_medica', methods=['POST'])
def consultar_guia_medica():
    """
    Endpoint para ElevenLabs Tool 2: Consultar guía médica (RAG)
    
    Body (JSON):
    {
        "pregunta": "¿Qué hago si tengo un ataque de pánico?",
        "top_k": 1  // OPCIONAL - Cuántos artículos retornar (default: 1)
    }
    
    Response:
    {
        "success": true,
        "respuesta_voz": "Para un ataque de pánico, aquí están los pasos...",
        "articulo": {...},
        "paginacion": {
            "total_disponibles": 5,
            "mostrando": 1,
            "hay_mas": true
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'pregunta' not in data:
            return jsonify({
                'success': False,
                'error': 'El parámetro "pregunta" es requerido',
                'respuesta_voz': 'Lo siento, necesito que me digas qué quieres saber.'
            }), 400
        
        pregunta = data['pregunta']
        top_k = data.get('top_k', 1)  # Por defecto solo 1 artículo
        
        logger.info(f"Consulta guia medica: '{pregunta}' (top_k={top_k})")
        
        # Buscar en base de conocimiento - buscar más para saber si hay otros disponibles
        logger.info(f"Llamando a knowledge_system.ask()...")
        resultados = get_knowledge_system().ask(pregunta, top_k=5, include_context=True)
        logger.info(f"Resultados obtenidos: {len(resultados) if resultados else 0}")
        
        if not resultados:
            logger.warning(f"No se encontraron resultados para: '{pregunta}'")
            return jsonify({
                'success': False,
                'respuesta_voz': 'Lo siento, no encontré información sobre eso. ¿Puedes reformular tu pregunta?',
                'pregunta': pregunta
            }), 200  # Cambiar a 200 para que no sea un error HTTP
        
        # Tomar solo los primeros top_k resultados para retornar
        resultados_a_mostrar = resultados[:top_k]
        total_disponibles = len(resultados)
        hay_mas = total_disponibles > top_k
        
        articulo = resultados_a_mostrar[0]
        tema = articulo.get('tema', 'Información')
        categoria = articulo.get('categoria', 'General')
        nivel_urgencia = articulo.get('nivel_urgencia', 'N/A')
        
        # Generar respuesta para voz (concisa y natural)
        respuesta_voz_parts = []
        
        # Intro
        if nivel_urgencia == 'CRÍTICO':
            respuesta_voz_parts.append(f"⚠️ ATENCIÓN: Esta es una situación crítica. ")
            # Agregar números de emergencia si existen
            if 'NUMEROS_EMERGENCIA' in articulo:
                numeros = articulo['NUMEROS_EMERGENCIA']
                if 'México' in numeros:
                    respuesta_voz_parts.append(f"Por favor llama inmediatamente al {numeros['México']}. ")
        
        respuesta_voz_parts.append(f"Sobre {tema}: ")
        
        # Descripción breve
        if 'descripcion_clinica' in articulo:
            desc = articulo['descripcion_clinica']
            # Limitar longitud para voz
            if len(desc) > 150:
                desc = desc[:147] + "..."
            respuesta_voz_parts.append(f"{desc} ")
        
        # Pasos inmediatos (máximo 3)
        pasos_key = 'PASOS_INMEDIATOS_CRÍTICOS' if 'PASOS_INMEDIATOS_CRÍTICOS' in articulo else 'pasos_inmediatos'
        if pasos_key in articulo:
            pasos = articulo[pasos_key][:3]  # Solo primeros 3
            respuesta_voz_parts.append("Aquí están los pasos que puedes seguir: ")
            for i, paso in enumerate(pasos, 1):
                if isinstance(paso, dict):
                    nombre = paso.get('nombre', paso.get('accion', ''))
                    respuesta_voz_parts.append(f"{i}. {nombre}. ")
        
        # Informar si hay más técnicas/recursos disponibles
        if hay_mas:
            respuesta_voz_parts.append(f"También tengo {total_disponibles - top_k} técnica{'s' if (total_disponibles - top_k) > 1 else ''} más relacionada{'s' if (total_disponibles - top_k) > 1 else ''} que te pueden ayudar. ¿Quieres conocerlas?")
        
        respuesta_voz = "".join(respuesta_voz_parts)
        
        # Formatear artículo completo para contexto (opcional)
        articulo_formateado = {
            'tema': tema,
            'categoria': categoria,
            'nivel_urgencia': nivel_urgencia,
            'descripcion': articulo.get('descripcion_clinica', ''),
            'sintomas': articulo.get('sintomas_clave', []),
            'pasos': articulo.get(pasos_key, []),
            'relevancia': articulo.get('relevancia', 'N/A'),
            'similarity_score': articulo.get('similarity_score', 0)
        }
        
        # Agregar números de emergencia si es crítico
        if nivel_urgencia == 'CRÍTICO' and 'NUMEROS_EMERGENCIA' in articulo:
            articulo_formateado['numeros_emergencia'] = articulo['NUMEROS_EMERGENCIA']
        
        response = {
            'success': True,
            'respuesta_voz': respuesta_voz,
            'pregunta': pregunta,
            'articulo': articulo_formateado,
            'paginacion': {
                'mostrando': len(resultados_a_mostrar),
                'total_disponibles': total_disponibles,
                'hay_mas': hay_mas,
                'siguiente_top_k': top_k + 1 if hay_mas else None
            }
        }
        
        logger.info(f"Retornando respuesta para consulta guia medica (mostrando {len(resultados_a_mostrar)} de {total_disponibles})")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error en consultar_guia_medica: {str(e)}")
        logger.exception(e)  # Esto imprime el stack trace completo
        return jsonify({
            'success': False,
            'error': str(e),
            'respuesta_voz': 'Lo siento, tuve un problema al consultar la guía médica. Por favor intenta de nuevo.'
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    # Para desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # Para producción, usar gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 api_rest:app
