"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BottomNav } from "@/components/bottom-nav"

interface Recurso {
  titulo: string
  contenido: string
  pregunta: string
  timestamp: string
}

export default function RecursosPage() {
  const [recursos, setRecursos] = useState<Recurso[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 1. Cargar recursos existentes
    const stored = localStorage.getItem('calma_recursos')
    if (stored) {
      try {
        const data = JSON.parse(stored)
        if (Array.isArray(data)) {
          setRecursos(data.slice().reverse()) // Mostrar los más nuevos primero
        }
      } catch (e) {
        console.error('Error parsing recursos:', e)
      }
    }
    setLoading(false)

    // 2. Escuchar nuevos recursos en tiempo real
    const handleNewRecurso = () => {
      const s = localStorage.getItem('calma_recursos')
      if (s) {
        try {
          const d = JSON.parse(s)
          if (Array.isArray(d)) setRecursos(d.slice().reverse())
        } catch (e) {
          console.error('Error parsing recursos on event:', e)
        }
      }
    }

    window.addEventListener('calma:recursos', handleNewRecurso)
    return () => window.removeEventListener('calma:recursos', handleNewRecurso)
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-white via-indigo-50/40 to-blue-50/40 page-transition">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-indigo-100 px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span className="text-sm font-medium text-gray-600">Calma - Recursos Guardados</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-6 overflow-y-auto pb-24 space-y-4">
        {recursos.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p className="text-lg font-medium text-gray-700">Tu caja de herramientas está vacía</p>
            <p className="text-sm mt-2">Cuando practiquemos técnicas o encuentre información útil, la guardaré aquí.</p>
          </div>
        ) : (
          recursos.map((recurso, index) => (
            <Card key={index} className="border-indigo-100 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <Badge variant="outline" className="mb-2 bg-blue-50 text-blue-700 border-blue-100">
                    Técnica
                  </Badge>
                  <span className="text-xs text-gray-400">
                    {new Date(recurso.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <CardTitle className="text-lg text-indigo-900">{recurso.titulo}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {recurso.contenido}
                </p>
                {recurso.pregunta && (
                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-400 italic">
                      Respuesta a: "{recurso.pregunta}"
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </main>

      <BottomNav />
    </div>
  )
}
