"use client"

import { useCallback, useEffect, useState } from "react"
import { useConversation } from "@elevenlabs/react"
import { BottomNav } from "@/components/bottom-nav"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Importar utils de testing (disponibles en window.calmaTest)
import "@/lib/test-utils"

interface Especialista {
  nombre: string
  especialidad: string
  costo?: string
  ubicacion?: string
  contacto?: string
}

interface Recurso {
  titulo: string
  contenido: string
  pregunta: string
  timestamp: string
}

export default function Page() {
  const [recentEspecialistas, setRecentEspecialistas] = useState<Especialista[]>([])
  const [recentRecursos, setRecentRecursos] = useState<Recurso[]>([])
  const [isMuted, setIsMuted] = useState(false)

  // ✅ Definir las funciones de Client Tools PRIMERO
  const guardarEspecialista = useCallback(async (parameters: { datos: string }) => {
    try {
      console.log("🛠️ Tool ejecutada: guardar_especialista", parameters)
      
      // Parseamos si viene como string, o usamos directo si llega como objeto
      const datosParsed = typeof parameters.datos === 'string' 
        ? JSON.parse(parameters.datos) 
        : parameters.datos
        
      localStorage.setItem('calma_recomendaciones', JSON.stringify(datosParsed))
      
      // Disparamos el evento para que la UI se actualice
      window.dispatchEvent(new CustomEvent('calma:recomendaciones', { 
        detail: datosParsed 
      }))
      
      // Actualizar tarjetas en tiempo real en la página principal
      if (datosParsed.resultados && Array.isArray(datosParsed.resultados)) {
        setRecentEspecialistas(datosParsed.resultados.slice(0, 3))
      }
      
      console.log("✅ Especialistas guardados exitosamente")
      return "Especialistas guardados con éxito en el dispositivo."
    } catch (error) {
      console.error("❌ Error guardando especialistas:", error)
      return "Hubo un error guardando los datos."
    }
  }, [])

  const guardarRecurso = useCallback(async (parameters: { titulo: string, contenido: string, pregunta?: string }) => {
    try {
      console.log("🛠️ Tool ejecutada: guardar_recurso", parameters)
      
      const recursos = JSON.parse(localStorage.getItem('calma_recursos') || '[]')
      
      const nuevoRecurso = {
        titulo: parameters.titulo,
        contenido: parameters.contenido,
        pregunta: parameters.pregunta || '',
        timestamp: new Date().toISOString()
      }
      
      recursos.push(nuevoRecurso)
      localStorage.setItem('calma_recursos', JSON.stringify(recursos))
      window.dispatchEvent(new CustomEvent('calma:recursos'))
      
      // Actualizar tarjetas en tiempo real en la página principal
      setRecentRecursos(prev => [nuevoRecurso, ...prev].slice(0, 2))
      
      console.log("✅ Recurso guardado exitosamente")
      return "Recurso guardado correctamente."
    } catch (error) {
      console.error("❌ Error guardando recurso:", error)
      return "Hubo un error guardando el recurso."
    }
  }, [])

  // ✅ Configuración del Hook de ElevenLabs con Client Tools
  const conversation = useConversation({
    // ✅ AQUÍ es donde se conectan las tools definidas en el Dashboard con tu código local
    clientTools: {
      guardar_especialista: guardarEspecialista,
      guardar_recurso: guardarRecurso
    },
    onConnect: () => {
      console.log('🔗 Conectado a ElevenLabs')
    },
    onDisconnect: () => {
      console.log('🔌 Desconectado de ElevenLabs')
    },
    onMessage: (message) => {
      console.log('📨 Mensaje recibido:', message)
    },
    onError: (error) => {
      console.error('❌ Error de ElevenLabs:', error)
    },
  })

  const conversationStatus = conversation.status
  const isSpeaking = conversation.isSpeaking

  // Manejar mute/unmute
  const toggleMute = useCallback(() => {
    const newMutedState = !isMuted
    setIsMuted(newMutedState)
    
    // Silenciar el audio del agente
    if (conversation && (conversation as any).setVolume) {
      (conversation as any).setVolume(newMutedState ? 0 : 1)
    }
  }, [isMuted, conversation])

  // Función para conectar/desconectar al tocar el Orbe
  const handleOrbClick = useCallback(async () => {
    if (conversationStatus === 'connected') {
      await conversation.endSession()
    } else {
      // Pide permisos de micrófono primero
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true })
        
        // ✅ Inicia la sesión con el AGENT ID
        // Las client tools YA están configuradas en el Dashboard de ElevenLabs
        // y mapeadas en el hook useConversation arriba
        await conversation.startSession({
          agentId: 'agent_6801kajzvktnemrtm1nxr93n92ed',
          connectionType: 'webrtc',
        })
      } catch (err) {
        console.error('Error iniciando sesión:', err)
        alert("Necesitamos permiso del micrófono para hablar contigo 🎤")
      }
    }
  }, [conversationStatus, conversation])

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/50 page-transition">
      {/* Main Content - Widget centered first, then content below */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-8 overflow-y-auto pb-24">
        <div className="w-full max-w-md flex flex-col items-center space-y-12">
          
          {/* SECCIÓN DEL ORBE PERSONALIZADO - Contenedor con altura fija */}
          <div className="flex flex-col items-center justify-center space-y-6 min-h-[280px]">
            
            {/* Estado en texto - Altura fija */}
            <div className="h-8 flex items-center justify-center">
              <span className={`text-sm font-medium tracking-wider uppercase transition-colors duration-300 ${
                conversationStatus === 'connected' ? 'text-indigo-600' : 'text-gray-400'
              }`}>
                {conversationStatus === 'connected' 
                  ? "Te escucho..." 
                  : "Toca para iniciar"}
              </span>
            </div>

            {/* EL ORBE GIGANTE INTERACTIVO - Sin cambiar tamaño del contenedor padre */}
            <div className="relative w-48 h-48 flex items-center justify-center">
              <button
                onClick={handleOrbClick}
                className={`
                  absolute inset-0 flex items-center justify-center 
                  w-48 h-48 rounded-full shadow-2xl transition-all duration-500 ease-out
                  focus:outline-none focus:ring-4 focus:ring-indigo-300
                  ${conversationStatus === 'connected' 
                    ? 'bg-gradient-to-br from-indigo-500 to-blue-600 scale-110 shadow-indigo-500/50' 
                    : 'bg-white border-4 border-indigo-100 hover:border-indigo-300 hover:scale-105 shadow-gray-200/50'}
                `}
                aria-label={conversationStatus === 'connected' ? "Terminar conversación" : "Iniciar conversación"}
              >
                {/* Animación de Ondas cuando habla */}
                {conversationStatus === 'connected' && (
                  <>
                    <div className={`absolute w-full h-full rounded-full bg-indigo-500 opacity-20 ${isSpeaking ? 'animate-ping' : 'animate-pulse'}`}></div>
                    <div className="absolute w-[120%] h-[120%] rounded-full border-2 border-indigo-200 opacity-30 animate-[spin_10s_linear_infinite]"></div>
                  </>
                )}

                {/* Ícono central (Micrófono) - Más pequeño */}
                <div className={`z-10 transition-colors duration-300 ${conversationStatus === 'connected' ? 'text-white' : 'text-indigo-400'}`}>
                  {conversationStatus === 'connected' ? (
                    // Micrófono activo
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                      <line x1="12" x2="12" y1="19" y2="23"/>
                      <line x1="8" x2="16" y1="23" y2="23"/>
                    </svg>
                  ) : (
                    // Micrófono inactivo
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                      <line x1="12" x2="12" y1="19" y2="22"/>
                    </svg>
                  )}
                </div>
              </button>

              {/* Botón de Mute - Solo visible cuando está conectado */}
              {conversationStatus === 'connected' && (
                <button
                  onClick={toggleMute}
                  className="absolute -bottom-2 -right-2 w-12 h-12 rounded-full bg-white border-2 border-indigo-200 shadow-lg flex items-center justify-center hover:bg-indigo-50 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 z-20 animate-[scaleIn_0.3s_ease-out]"
                  aria-label={isMuted ? "Activar audio" : "Silenciar audio"}
                >
                  {isMuted ? (
                    // Icono de audio silenciado
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-500">
                      <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                      <line x1="23" y1="9" x2="17" y2="15"/>
                      <line x1="17" y1="9" x2="23" y2="15"/>
                    </svg>
                  ) : (
                    // Icono de audio activo
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-600">
                      <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                      <path d="M15.54 8.46a5 5 0 010 7.07"/>
                      <path d="M19.07 4.93a10 10 0 010 14.14"/>
                    </svg>
                  )}
                </button>
              )}
            </div>

          </div>

          {/* Welcome Section - Below widget */}
          <div className="w-full text-center space-y-8">
            <div className="space-y-3">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">Calma</h1>
              <p className="text-gray-600 text-base">Tu compañero de bienestar mental</p>
            </div>
            
            <div className="space-y-4 text-left">
              {/* Tarjeta Principal con animación */}
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg shadow-indigo-100/50 border border-indigo-100 space-y-3 animate-[fadeIn_0.6s_ease-out]">
                <h2 className="font-semibold text-indigo-900 text-lg">¿Cómo puedo ayudarte?</h2>
                <p className="text-sm text-gray-600">
                  Puedo ayudarte a encontrar especialistas en salud mental y proporcionarte información sobre:
                </p>
                <ul className="text-sm text-gray-600 space-y-2 ml-1">
                  <li className="flex items-center gap-2 animate-[slideIn_0.4s_ease-out_0.1s_both]">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                    Búsqueda de psicólogos y terapeutas
                  </li>
                  <li className="flex items-center gap-2 animate-[slideIn_0.4s_ease-out_0.2s_both]">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    Manejo de ansiedad y estrés
                  </li>
                  <li className="flex items-center gap-2 animate-[slideIn_0.4s_ease-out_0.3s_both]">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                    Técnicas de relajación
                  </li>
                  <li className="flex items-center gap-2 animate-[slideIn_0.4s_ease-out_0.4s_both]">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    Recursos de apoyo emocional
                  </li>
                </ul>
              </div>

              {/* Tarjetas dinámicas de Especialistas */}
              {recentEspecialistas.length > 0 && (
                <div className="space-y-3 animate-[slideUp_0.5s_ease-out]">
                  <h3 className="text-sm font-semibold text-indigo-800 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
                    </svg>
                    Especialistas Recomendados
                  </h3>
                  {recentEspecialistas.map((esp, idx) => (
                    <Card 
                      key={idx} 
                      className="border-green-100 bg-gradient-to-br from-green-50/80 to-emerald-50/80 backdrop-blur-sm shadow-md animate-[scaleIn_0.4s_ease-out] hover:shadow-lg transition-shadow"
                      style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-start gap-2">
                          <div className="flex-1">
                            <CardTitle className="text-base text-green-900">{esp.nombre}</CardTitle>
                            <Badge variant="outline" className="mt-1 bg-green-100 text-green-700 border-green-200 text-xs">
                              {esp.especialidad}
                            </Badge>
                          </div>
                          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0 space-y-1">
                        {esp.costo && (
                          <p className="text-xs text-gray-600 flex items-center gap-1">
                            <span className="font-medium">💰</span> {esp.costo}
                          </p>
                        )}
                        {esp.ubicacion && (
                          <p className="text-xs text-gray-600 flex items-center gap-1">
                            <span className="font-medium">📍</span> {esp.ubicacion}
                          </p>
                        )}
                        {esp.contacto && (
                          <p className="text-xs text-gray-600 flex items-center gap-1">
                            <span className="font-medium">📞</span> {esp.contacto}
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {/* Tarjetas dinámicas de Recursos */}
              {recentRecursos.length > 0 && (
                <div className="space-y-3 animate-[slideUp_0.5s_ease-out]">
                  <h3 className="text-sm font-semibold text-blue-800 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
                    </svg>
                    Recursos Útiles
                  </h3>
                  {recentRecursos.map((recurso, idx) => (
                    <Card 
                      key={idx}
                      className="border-blue-100 bg-gradient-to-br from-blue-50/80 to-indigo-50/80 backdrop-blur-sm shadow-md animate-[scaleIn_0.4s_ease-out] hover:shadow-lg transition-shadow"
                      style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                      <CardHeader className="pb-2">
                        <div className="flex items-start gap-2">
                          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                          </div>
                          <div className="flex-1">
                            <CardTitle className="text-sm text-blue-900 leading-snug">{recurso.titulo}</CardTitle>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
                          {recurso.contenido}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
