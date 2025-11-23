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
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent"></div>
          <span className="text-sm font-medium text-muted-foreground">Calma</span>
        </div>
        <button className="text-muted-foreground hover:text-foreground transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-start px-6 py-8 gap-8 overflow-y-auto">
        {/* Welcome Section - Now Visible Above Widget */}
        <div className="w-full max-w-md text-center pt-4">
          <h2 className="text-2xl font-semibold text-foreground mb-4">¡Bienvenido a Calma!</h2>
        </div>

        {/* Made the widget smaller by reducing max-w and constraining size */}
        <div className="w-20 h-20 flex items-center justify-center">
          <elevenlabs-convai agent-id="agent_6801kajzvktnemrtm1nxr93n92ed"></elevenlabs-convai>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
