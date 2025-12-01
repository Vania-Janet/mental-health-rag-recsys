"use client"

import { motion } from "framer-motion"

interface ContextCardProps {
  type: "exercise" | "doctor" | null
  onClose: () => void
}

export function ContextCard({ type, onClose }: ContextCardProps) {
  if (!type) return null

  const exercises = {
    exercise: {
      title: "Respiración Cuadrada",
      description: "Respiración cuadrada para calmar tu mente",
      steps: [
        { number: 1, label: "Inhala durante 4 segundos" },
        { number: 2, label: "Aguanta durante 4 segundos" },
        { number: 3, label: "Exhala durante 4 segundos" },
      ],
    },
  }

  const content = exercises[type] || exercises.exercise

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="bg-card border border-border rounded-lg p-6 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-foreground">{content.title}</h3>
          <p className="text-xs text-muted-foreground mt-1">{content.description}</p>
        </div>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors p-1 -mr-1 -mt-1"
          aria-label="Close card"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Steps */}
      <div className="space-y-2 mb-4">
        {content.steps.map((step) => (
          <div key={step.number} className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-medium text-accent">{step.number}</span>
            </div>
            <p className="text-sm text-foreground">{step.label}</p>
          </div>
        ))}
      </div>

      {/* Action Button */}
      <button
        onClick={onClose}
        className="w-full py-2 px-3 text-sm font-medium text-foreground bg-primary/10 hover:bg-primary/20 rounded-md transition-colors border border-primary/20"
      >
        Start Exercise
      </button>
    </motion.div>
  )
}
