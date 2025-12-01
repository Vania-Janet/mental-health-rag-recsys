/**
 * Sistema de integración con ElevenLabs Conversational AI
 * 
 * Este módulo captura las respuestas de las herramientas (tools) de ElevenLabs
 * y las guarda en localStorage para su visualización en la página de especialistas.
 */

export interface ToolResponse {
  tool: string
  parameters: Record<string, any>
  response: any
  timestamp: string
}

export interface RecommendationData {
  searchParams: {
    sintoma?: string
    genero?: string
    presupuesto?: string
    ubicacion?: string
    consulta?: string
  }
  especialistas?: Array<{
    nombre: string
    especialidad: string
    ubicacion: string
    telefono: string
    correo: string
    sitio_web: string
    horario: string
    costo_consulta: string
    calificacion: number
    idiomas: string[]
    genero_especialista: string
    es_emergencia?: boolean
    descripcion?: string
  }>
  guia_medica?: {
    respuesta: string
    pasos: string[]
    fuentes?: string[]
  }
  nivel_crisis?: 'CRITICO' | 'ALTO' | 'NORMAL'
  timestamp: string
}

/**
 * Inicializa el listener de ElevenLabs
 * Debe ser llamado al montar el componente que contiene el widget
 */
export function initializeElevenLabsListener() {
  // Listener para respuestas de herramientas
  if (typeof window !== 'undefined') {
    // @ts-ignore - ElevenLabs SDK no tiene tipos oficiales
    if (window.ElevenLabs) {
      console.log('✅ ElevenLabs SDK detected')
      
      // Hook para capturar respuestas de tools
      // @ts-ignore
      const originalFetch = window.fetch
      // @ts-ignore
      window.fetch = async (...args) => {
        const response = await originalFetch(...args)
        
        // Interceptar respuestas de la API de ElevenLabs
        const url = args[0]?.toString() || ''
        if (url.includes('elevenlabs.io') || url.includes('api.elevenlabs.ai')) {
          const clone = response.clone()
          clone.json().then((data) => {
            handleElevenLabsResponse(data)
          }).catch(() => {
            // No es JSON, ignorar
          })
        }
        
        return response
      }
    }
    
    // También escuchar eventos personalizados que podría emitir el widget
    window.addEventListener('elevenlabs:tool-response', (event: any) => {
      handleElevenLabsResponse(event.detail)
    })
    
    console.log('🎧 ElevenLabs listeners initialized')
  }
}

/**
 * Maneja las respuestas de las herramientas de ElevenLabs
 */
function handleElevenLabsResponse(data: any) {
  console.log('📥 ElevenLabs response:', data)
  
  // Detectar qué herramienta se llamó
  if (data.tool_name === 'buscar_especialista' || data.tool === 'buscar_especialista') {
    handleBuscarEspecialistaResponse(data)
  } else if (data.tool_name === 'consultar_guia_medica' || data.tool === 'consultar_guia_medica') {
    handleConsultarGuiaMedicaResponse(data)
  }
}

/**
 * Procesa respuesta de buscar_especialista
 */
function handleBuscarEspecialistaResponse(data: any) {
  const params = data.parameters || data.params || {}
  const response = data.response || data.result || {}
  
  const recommendationData: RecommendationData = {
    searchParams: {
      sintoma: params.sintoma || params.symptom,
      genero: params.genero || params.gender,
      presupuesto: params.presupuesto || params.budget,
      ubicacion: params.ubicacion || params.location,
    },
    especialistas: response.especialistas || response.specialists || [],
    nivel_crisis: response.nivel_crisis || response.crisis_level,
    timestamp: new Date().toISOString(),
  }
  
  // Guardar en localStorage
  localStorage.setItem('calma_recomendaciones', JSON.stringify(recommendationData))
  
  // Disparar evento personalizado para que el componente se actualice
  const event = new CustomEvent('calma:recomendaciones', { detail: recommendationData })
  window.dispatchEvent(event)
  
  console.log('💾 Recommendations saved:', recommendationData)
}

/**
 * Procesa respuesta de consultar_guia_medica
 */
function handleConsultarGuiaMedicaResponse(data: any) {
  const params = data.parameters || data.params || {}
  const response = data.response || data.result || {}
  
  // Obtener recomendaciones existentes o crear nuevas
  const existing = localStorage.getItem('calma_recomendaciones')
  let recommendationData: RecommendationData
  
  if (existing) {
    recommendationData = JSON.parse(existing)
  } else {
    recommendationData = {
      searchParams: {},
      timestamp: new Date().toISOString(),
    }
  }
  
  // Agregar información de la guía médica
  recommendationData.searchParams.consulta = params.consulta || params.query
  recommendationData.guia_medica = {
    respuesta: response.respuesta || response.answer || '',
    pasos: response.pasos || response.steps || [],
    fuentes: response.fuentes || response.sources || [],
  }
  
  // Guardar
  localStorage.setItem('calma_recomendaciones', JSON.stringify(recommendationData))
  
  const event = new CustomEvent('calma:recomendaciones', { detail: recommendationData })
  window.dispatchEvent(event)
  
  console.log('💾 Medical guide saved:', recommendationData)
}

/**
 * Limpia las recomendaciones guardadas
 */
export function clearRecommendations() {
  localStorage.removeItem('calma_recomendaciones')
  const event = new CustomEvent('calma:recomendaciones', { detail: null })
  window.dispatchEvent(event)
  console.log('🗑️  Recommendations cleared')
}

/**
 * Obtiene las recomendaciones guardadas
 */
export function getStoredRecommendations(): RecommendationData | null {
  if (typeof window === 'undefined') return null
  
  const stored = localStorage.getItem('calma_recomendaciones')
  if (!stored) return null
  
  try {
    return JSON.parse(stored)
  } catch (error) {
    console.error('Error parsing recommendations:', error)
    return null
  }
}

/**
 * Método manual para testear guardando recomendaciones de prueba
 */
export function testSaveRecommendations() {
  const testData: RecommendationData = {
    searchParams: {
      sintoma: 'ansiedad',
      genero: 'cualquiera',
      presupuesto: 'medio',
      ubicacion: 'Benito Juárez',
    },
    especialistas: [
      {
        nombre: 'Dra. Ana García Rodríguez',
        especialidad: 'Psiquiatra - Crisis y Emergencias',
        ubicacion: 'Colonia del Valle, Benito Juárez',
        telefono: '55-CRISIS-01',
        correo: 'crisis1@saludmental.cdmx.gob.mx',
        sitio_web: 'https://saludmental.cdmx.gob.mx/crisis',
        horario: '24/7 - Disponibilidad inmediata',
        costo_consulta: '$500 - $800',
        calificacion: 4.9,
        idiomas: ['Español', 'Inglés'],
        genero_especialista: 'femenino',
        es_emergencia: true,
        descripcion: 'Especialista en intervención de crisis con 15 años de experiencia',
      },
    ],
    nivel_crisis: 'ALTO',
    timestamp: new Date().toISOString(),
  }
  
  localStorage.setItem('calma_recomendaciones', JSON.stringify(testData))
  const event = new CustomEvent('calma:recomendaciones', { detail: testData })
  window.dispatchEvent(event)
  
  console.log('🧪 Test recommendations saved!')
  return testData
}

/**
 * Hook de React para usar en componentes
 */
export function useRecommendations() {
  if (typeof window === 'undefined') {
    return { recommendations: null, clearRecommendations }
  }
  
  return {
    recommendations: getStoredRecommendations(),
    clearRecommendations,
    testSaveRecommendations,
  }
}
