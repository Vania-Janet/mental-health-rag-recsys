"use client"

import { useEffect } from "react"
import { BottomNav } from "@/components/bottom-nav"
import { initializeElevenLabsListener } from "@/lib/elevenlabs-integration"

export default function Page() {
  useEffect(() => {
    const script = document.createElement("script")
    script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed"
    script.async = true
    script.setAttribute("data-lang", "es")
    
    // Inicializar listener cuando el script cargue
    script.onload = () => {
      console.log('📡 ElevenLabs widget loaded')
      initializeElevenLabsListener()
    }
    
    document.body.appendChild(script)
    
    return () => {
      // Cleanup
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/50">
      {/* Main Content - Widget centered first, then content below */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-8 overflow-y-auto pb-24">
        <div className="w-full max-w-md flex flex-col items-center space-y-12">
          
          {/* Voice Assistant Widget - Centered prominently */}
          <div className="flex justify-center items-center w-full">
            <elevenlabs-convai agent-id="agent_6801kajzvktnemrtm1nxr93n92ed"></elevenlabs-convai>
          </div>

          {/* Welcome Section - Below widget */}
          <div className="w-full text-center space-y-8">
            <div className="space-y-3">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">Calma</h1>
              <p className="text-gray-600 text-base">Tu compañero de bienestar mental</p>
            </div>
            
            <div className="space-y-4 text-left">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg shadow-indigo-100/50 border border-indigo-100 space-y-3">
                <h2 className="font-semibold text-indigo-900 text-lg">¿Cómo puedo ayudarte?</h2>
                <p className="text-sm text-gray-600">
                  Puedo ayudarte a encontrar especialistas en salud mental y proporcionarte información sobre:
                </p>
                <ul className="text-sm text-gray-600 space-y-2 ml-1">
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                    Búsqueda de psicólogos y terapeutas
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    Manejo de ansiedad y estrés
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                    Técnicas de relajación
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    Recursos de apoyo emocional
                  </li>
                </ul>
              </div>
            </div>
          </div>

        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
