"use client"

import { motion } from "framer-motion"

interface PulsingOrbProps {
  isListening: boolean
  onClick: () => void
}

export function PulsingOrb({ isListening, onClick }: PulsingOrbProps) {
  return (
    <button
      onClick={onClick}
      className="relative w-32 h-32 rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-background transition-all"
      aria-label={isListening ? "Stop listening" : "Start listening"}
    >
      {/* Outer pulsing ring - only visible when listening */}
      {isListening && (
        <>
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-accent opacity-60"
            animate={{
              scale: [1, 1.3],
              opacity: [0.6, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Number.POSITIVE_INFINITY,
              ease: "easeOut",
            }}
          />
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-accent opacity-40"
            animate={{
              scale: [1, 1.2],
              opacity: [0.4, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Number.POSITIVE_INFINITY,
              ease: "easeOut",
              delay: 0.3,
            }}
          />
        </>
      )}

      {/* Main orb */}
      <motion.div
        className={`absolute inset-0 rounded-full ${
          isListening ? "bg-gradient-to-br from-accent to-accent/80" : "bg-gradient-to-br from-primary to-primary/80"
        } shadow-lg`}
        animate={
          isListening
            ? {
                boxShadow: [
                  "0 0 20px rgba(130, 167, 189, 0.3)",
                  "0 0 40px rgba(130, 167, 189, 0.6)",
                  "0 0 20px rgba(130, 167, 189, 0.3)",
                ],
              }
            : {
                boxShadow: [
                  "0 0 10px rgba(27, 75, 95, 0.2)",
                  "0 0 15px rgba(27, 75, 95, 0.3)",
                  "0 0 10px rgba(27, 75, 95, 0.2)",
                ],
              }
        }
        transition={{
          duration: isListening ? 1.5 : 2.5,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      />

      {/* Inner glow effect */}
      <motion.div
        className={`absolute inset-2 rounded-full ${isListening ? "bg-accent/20" : "bg-primary/10"}`}
        animate={{
          opacity: isListening ? [0.4, 0.8] : [0.3, 0.6],
        }}
        transition={{
          duration: isListening ? 1.5 : 2.5,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      />

      {/* Center dot */}
      <motion.div
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white/30"
        animate={{
          scale: isListening ? [1, 1.2, 1] : [1, 1.1, 1],
        }}
        transition={{
          duration: isListening ? 1.5 : 2.5,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      />
    </button>
  )
}
