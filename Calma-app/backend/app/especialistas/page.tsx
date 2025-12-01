"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { BottomNav } from "@/components/bottom-nav"

interface Especialista {
  id: string
  nombre: string
  tipo_profesional: string
  modalidad: string
  ubicacion: {
    colonia?: string
    delegacion?: string
    latitud?: string
    longitud?: string
  }
  costo: string
  costo_min?: number
  rating: number
  resenas: number
  especializaciones: string[]
  grupo_etario: string[]
  contacto: {
    telefono?: string
    email?: string
    website?: string
  }
  disponibilidad: string
  metodos_pago: string[]
  scores?: {
    relevance: number
    similarity: number
  }
}

interface RecommendationData {
  sintoma?: string
  alerta_crisis?: boolean
  nivel_urgencia?: string
  numeros_emergencia?: {
    mexico?: string
    emergencia_general?: string
    mensaje?: string
  }
  parametros?: {
    sintoma?: string
    genero?: string
    presupuesto?: string
    ubicacion?: string
  }
  total_resultados: number
  resultados: Especialista[]
  timestamp?: string
}

export default function EspecialistasPage() {
  const [recommendations, setRecommendations] = useState<RecommendationData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Intentar cargar recomendaciones desde localStorage
    const stored = localStorage.getItem('calma_recomendaciones')
    if (stored) {
      try {
        const data = JSON.parse(stored)
        setRecommendations(data)
      } catch (e) {
        console.error('Error parsing recommendations:', e)
      }
    }
    setLoading(false)

    // Escuchar eventos de nuevas recomendaciones
    const handleNewRecommendations = (event: CustomEvent) => {
      setRecommendations(event.detail)
      localStorage.setItem('calma_recomendaciones', JSON.stringify(event.detail))
    }

    window.addEventListener('calma:recomendaciones' as any, handleNewRecommendations as any)
    
    return () => {
      window.removeEventListener('calma:recomendaciones' as any, handleNewRecommendations as any)
    }
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 page-transition">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando recomendaciones...</p>
        </div>
      </div>
    )
  }

  if (!recommendations || recommendations.total_resultados === 0) {
    return (
      <div className="flex flex-col h-screen bg-gradient-to-br from-white via-indigo-50/40 to-blue-50/40">
        <main className="flex-1 flex items-center justify-center p-6 pb-24">
          <Card className="max-w-md w-full border-indigo-100 shadow-lg">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <CardTitle className="text-indigo-900">Sin Recomendaciones</CardTitle>
              <CardDescription>
                Aún no hay especialistas recomendados. Habla con Calma y automáticamente guardará los especialistas que te recomiende aquí.
              </CardDescription>
            </CardHeader>
          </Card>
        </main>
        <BottomNav />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-white via-indigo-50/40 to-blue-50/40 transition-all duration-300">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-indigo-100">
        <div className="container max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-indigo-600"></div>
            <div>
              <h1 className="text-lg font-semibold text-indigo-900">Especialistas Recomendados</h1>
              <p className="text-xs text-gray-600">
                {recommendations.total_resultados} especialista{recommendations.total_resultados !== 1 ? 's' : ''} encontrado{recommendations.total_resultados !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Alerta de Crisis */}
        {recommendations.alerta_crisis && (
          <Alert variant="destructive" className="border-2">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">⚠️ Nivel de Urgencia: {recommendations.nivel_urgencia}</h3>
                <AlertDescription className="space-y-2">
                  {recommendations.numeros_emergencia && (
                    <div className="space-y-1 text-sm">
                      <p className="font-medium">{recommendations.numeros_emergencia.mensaje}</p>
                      <div className="flex flex-col gap-1 mt-2">
                        {recommendations.numeros_emergencia.mexico && (
                          <a href={`tel:${recommendations.numeros_emergencia.mexico.split(' ')[0]}`} className="inline-flex items-center gap-2 text-white hover:underline">
                            📞 {recommendations.numeros_emergencia.mexico}
                          </a>
                        )}
                        {recommendations.numeros_emergencia.emergencia_general && (
                          <a href={`tel:${recommendations.numeros_emergencia.emergencia_general}`} className="inline-flex items-center gap-2 text-white hover:underline">
                            🚨 {recommendations.numeros_emergencia.emergencia_general}
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </AlertDescription>
              </div>
            </div>
          </Alert>
        )}

        {/* Parámetros de Búsqueda */}
        {recommendations.parametros && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Búsqueda Realizada</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {recommendations.parametros.sintoma && recommendations.parametros.sintoma !== 'no especificado' && (
                  <Badge variant="outline">
                    <span className="text-muted-foreground mr-1">Síntoma:</span> {recommendations.parametros.sintoma}
                  </Badge>
                )}
                {recommendations.parametros.genero && recommendations.parametros.genero !== 'no especificado' && (
                  <Badge variant="outline">
                    <span className="text-muted-foreground mr-1">Género:</span> {recommendations.parametros.genero}
                  </Badge>
                )}
                {recommendations.parametros.presupuesto && recommendations.parametros.presupuesto !== 'no especificado' && (
                  <Badge variant="outline">
                    <span className="text-muted-foreground mr-1">Presupuesto:</span> {recommendations.parametros.presupuesto}
                  </Badge>
                )}
                {recommendations.parametros.ubicacion && recommendations.parametros.ubicacion !== 'no especificado' && (
                  <Badge variant="outline">
                    <span className="text-muted-foreground mr-1">Ubicación:</span> {recommendations.parametros.ubicacion}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Lista de Especialistas */}
        <div className="space-y-4">
          {recommendations.resultados.map((especialista, index) => (
            <Card key={especialista.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {index === 0 && (
                        <Badge className="bg-accent text-accent-foreground">Recomendado</Badge>
                      )}
                      <Badge variant="outline">{especialista.modalidad}</Badge>
                    </div>
                    <CardTitle className="text-xl">{especialista.nombre}</CardTitle>
                    <CardDescription className="mt-1">
                      {especialista.tipo_profesional}
                    </CardDescription>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="flex items-center gap-1">
                      <svg className="w-4 h-4 text-yellow-500 fill-current" viewBox="0 0 24 24">
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                      </svg>
                      <span className="font-semibold">{especialista.rating}</span>
                      <span className="text-xs text-muted-foreground">({especialista.resenas})</span>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Ubicación y Costo */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span className="font-medium">Ubicación:</span>
                    </div>
                    <p className="text-sm text-muted-foreground ml-6">
                      {especialista.ubicacion.colonia && `${especialista.ubicacion.colonia}, `}
                      {especialista.ubicacion.delegacion || 'Online'}
                    </p>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium">Costo:</span>
                    </div>
                    <p className="text-sm text-muted-foreground ml-6">
                      {especialista.costo}
                    </p>
                  </div>
                </div>

                <Separator />

                {/* Especializaciones */}
                {especialista.especializaciones && especialista.especializaciones.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Especializaciones:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {especialista.especializaciones.slice(0, 5).map((esp, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {esp}
                        </Badge>
                      ))}
                      {especialista.especializaciones.length > 5 && (
                        <Badge variant="secondary" className="text-xs">
                          +{especialista.especializaciones.length - 5} más
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Disponibilidad */}
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">Disponibilidad:</span>
                  </div>
                  <p className="text-sm text-muted-foreground ml-6">
                    {especialista.disponibilidad}
                  </p>
                </div>

                {/* Métodos de Pago */}
                {especialista.metodos_pago && especialista.metodos_pago.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Métodos de pago:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {especialista.metodos_pago.map((metodo, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {metodo}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <Separator />

                {/* Contacto */}
                <div className="flex flex-wrap gap-2">
                  {especialista.contacto.telefono && (
                    <Button asChild size="sm" className="bg-accent hover:bg-accent/90">
                      <a href={`tel:${especialista.contacto.telefono}`}>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                        Llamar
                      </a>
                    </Button>
                  )}
                  {especialista.contacto.email && (
                    <Button asChild size="sm" variant="outline">
                      <a href={`mailto:${especialista.contacto.email}`}>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        Email
                      </a>
                    </Button>
                  )}
                  {especialista.contacto.website && (
                    <Button asChild size="sm" variant="outline">
                      <a href={`https://${especialista.contacto.website.replace(/^https?:\/\//, '')}`} target="_blank" rel="noopener noreferrer">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                        Sitio Web
                      </a>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Footer */}
        <Card className="bg-muted/50">
          <CardContent className="pt-6 text-center text-sm text-muted-foreground">
            <p>
              💙 Recuerda que estos son solo especialistas recomendados. Siempre verifica las credenciales antes de iniciar tratamiento.
            </p>
            <p className="mt-2">
              Para emergencias, llama al <a href="tel:800-911-2000" className="text-accent hover:underline font-medium">800-911-2000</a>
            </p>
          </CardContent>
        </Card>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
