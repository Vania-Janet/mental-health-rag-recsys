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
      {/* Voice Assistant Widget - Positioned at top center */}
      <div className="w-full flex flex-col items-center gap-3 pt-6 pb-4 px-6 bg-white/60 backdrop-blur-sm border-b border-indigo-100">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-blue-500 animate-pulse"></div>
          <span className="text-lg font-semibold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">Calma</span>
        </div>
        <p className="text-sm text-indigo-600 font-medium text-center">
          👋 Presiona el orbe para hablar conmigo
        </p>
        <div className="flex justify-center items-center w-full">
          <elevenlabs-convai agent-id="agent_6801kajzvktnemrtm1nxr93n92ed"></elevenlabs-convai>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-start px-6 py-8 overflow-y-auto pb-20">
        {/* Welcome Section */}
        <div className="w-full max-w-md text-center space-y-8 pt-12">
          <div className="space-y-4">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-blue-500 shadow-xl shadow-indigo-500/30">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
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

      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
