"use client"

import { useState, useEffect } from "react"
import { usePathname, useRouter } from "next/navigation"

export function BottomNav() {
  const pathname = usePathname()
  const router = useRouter()
  const [hasRecommendations, setHasRecommendations] = useState(false)

  // Detectar la ruta activa
  const getActiveRoute = () => {
    if (pathname === "/especialistas") return "especialistas"
    if (pathname === "/recursos") return "recursos"
    return "home"
  }

  const [active, setActive] = useState<"home" | "recursos" | "especialistas">(getActiveRoute())

  useEffect(() => {
    // Verificar si hay recomendaciones guardadas
    const checkRecommendations = () => {
      const stored = localStorage.getItem('calma_recomendaciones')
      setHasRecommendations(!!stored)
    }

    checkRecommendations()

    // Escuchar nuevas recomendaciones
    const handleNewRecs = () => checkRecommendations()
    window.addEventListener('calma:recomendaciones', handleNewRecs)
    
    return () => window.removeEventListener('calma:recomendaciones', handleNewRecs)
  }, [])

  const navItems = [
    { id: "recursos" as const, label: "Recursos", icon: "recursos", path: "/recursos" },
    { id: "home" as const, label: "Inicio", icon: "home", path: "/" },
    { id: "especialistas" as const, label: "Especialistas", icon: "especialistas", path: "/especialistas" },
  ]

  const icons: Record<string, React.ReactElement> = {
    recursos: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
        />
      </svg>
    ),
    home: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h2m14-5v5a1 1 0 01-1 1h-2m0-7V9m0 0L9 5"
        />
      </svg>
    ),
    especialistas: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
    ),
  }

  const handleNavClick = (id: "home" | "recursos" | "especialistas", path: string) => {
    setActive(id)
    router.push(path)
  }

  return (
    <nav className="border-t border-border bg-background/50 backdrop-blur-sm">
      <div className="flex items-center justify-around">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => handleNavClick(item.id, item.path)}
            className={`flex-1 flex flex-col items-center justify-center py-4 transition-colors relative ${
              active === item.id ? "text-accent" : "text-muted-foreground hover:text-foreground"
            }`}
            aria-label={item.label}
          >
            {icons[item.icon]}
            <span className="text-xs mt-1 font-medium">{item.label}</span>
            {/* Badge de notificación para especialistas */}
            {item.id === "especialistas" && hasRecommendations && active !== "especialistas" && (
              <span className="absolute top-2 right-1/4 w-2 h-2 bg-accent rounded-full"></span>
            )}
          </button>
        ))}
      </div>
    </nav>
  )
}
