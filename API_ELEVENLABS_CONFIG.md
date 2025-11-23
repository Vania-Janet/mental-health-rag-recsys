# Configuración de Tools para ElevenLabs - API Calma

## 🔧 Tool 1: Buscar Especialista (Primera Búsqueda)

**Nombre del Tool:** `buscar_especialista`

**URL del Endpoint:** `https://tu-api.onrender.com/buscar_especialista`

**Método:** POST

**Descripción para ElevenLabs:**
```
Busca especialistas en salud mental (psicólogos, psiquiatras, terapeutas) basándose en los síntomas del usuario, presupuesto, género preferido y ubicación. Usa este tool cuando el usuario menciona por primera vez qué tipo de ayuda necesita.
```

**Parámetros:**

1. **sintoma** (string, REQUERIDO)
   - Descripción: El problema, síntoma o motivo de consulta del usuario
   - Ejemplo: "ansiedad", "depresión", "estrés laboral", "problemas de pareja"

2. **genero** (string, OPCIONAL)
   - Descripción: Género preferido del especialista
   - Ejemplo: "mujer", "hombre", "cualquiera"

3. **presupuesto** (string, OPCIONAL)
   - Descripción: Restricción económica del usuario
   - Ejemplo: "barato", "gratis", "económico", "accesible", "medio", "sin restricción"

4. **ubicacion** (string, OPCIONAL)
   - Descripción: Zona o delegación preferida en CDMX
   - Ejemplo: "Coyoacán", "Roma", "Polanco", "Centro"

**Cuándo usar:** 
- Primera vez que el usuario pregunta por especialistas
- Cuando el usuario cambia completamente los criterios de búsqueda

---

## 🔧 Tool 2: Obtener Más Especialistas

**Nombre del Tool:** `mas_especialistas`

**URL del Endpoint:** `https://tu-api.onrender.com/mas_especialistas`

**Método:** POST

**Descripción para ElevenLabs:**
```
Obtiene especialistas adicionales cuando el usuario pide "más opciones", "otros especialistas" o "dame más". Mantiene los mismos criterios de búsqueda originales pero muestra diferentes resultados. IMPORTANTE: Usa los mismos parámetros de la búsqueda anterior.
```

**Parámetros:**

1. **sintoma** (string, REQUERIDO)
   - Descripción: El mismo síntoma de la búsqueda anterior
   - Ejemplo: "ansiedad"

2. **genero** (string, OPCIONAL)
   - Descripción: El mismo género de la búsqueda anterior
   - Ejemplo: "mujer"

3. **presupuesto** (string, OPCIONAL)
   - Descripción: El mismo presupuesto de la búsqueda anterior
   - Ejemplo: "barato"

4. **ubicacion** (string, OPCIONAL)
   - Descripción: La misma ubicación de la búsqueda anterior
   - Ejemplo: "Coyoacán"

5. **offset** (number, OPCIONAL, default: 3)
   - Descripción: Desde qué resultado comenzar (3 para la segunda página, 6 para la tercera, etc.)
   - Ejemplo: 3, 6, 9

**Cuándo usar:**
- Cuando el usuario dice: "dame más", "muéstrame otros", "hay más opciones?"
- Cuando el usuario no está satisfecho con las primeras opciones
- IMPORTANTE: Mantén los parámetros originales de la primera búsqueda

**Ejemplo de uso secuencial:**
```
Usuario: "Necesito ayuda con ansiedad en Coyoacán, algo económico"
→ Usar buscar_especialista con sintoma="ansiedad", ubicacion="Coyoacán", presupuesto="económico"

Usuario: "Dame más opciones"
→ Usar mas_especialistas con los MISMOS parámetros + offset=3

Usuario: "¿Hay más?"
→ Usar mas_especialistas con los MISMOS parámetros + offset=6
```

---

## 🔧 Tool 3: Consultar Guía Médica

**Nombre del Tool:** `consultar_guia_medica`

**URL del Endpoint:** `https://tu-api.onrender.com/consultar_guia_medica`

**Método:** POST

**Descripción para ElevenLabs:**
```
Consulta la base de conocimiento sobre qué hacer en situaciones de salud mental. Proporciona pasos inmediatos, técnicas de respiración, información sobre crisis, etc. Usa este tool cuando el usuario pregunta QUÉ HACER, no cuando busca UN ESPECIALISTA.
```

**Parámetros:**

1. **pregunta** (string, REQUERIDO)
   - Descripción: La pregunta del usuario sobre qué hacer o cómo manejar una situación
   - Ejemplo: "¿Qué hago si tengo un ataque de pánico?", "¿Cómo puedo calmarme cuando tengo ansiedad?"

**Cuándo usar:**
- Cuando el usuario pregunta "¿qué hago si...?"
- Cuando busca técnicas o pasos inmediatos
- Cuando pregunta sobre síntomas o cómo manejar una crisis
- NO uses este tool si el usuario quiere encontrar un especialista

---

## 📋 Instrucciones para el Agente de ElevenLabs

**Contexto del Sistema:**
Eres Calma, un asistente de voz empático especializado en salud mental. Tu objetivo es ayudar a las personas a encontrar especialistas y proporcionar información sobre qué hacer en situaciones de salud mental.

**Reglas importantes:**

1. **Primera búsqueda:** Siempre usa `buscar_especialista` la primera vez
2. **Más resultados:** Cuando el usuario pida más opciones, usa `mas_especialistas` con los MISMOS parámetros
3. **Contexto:** Recuerda los parámetros de búsqueda originales (sintoma, género, presupuesto, ubicación)
4. **Paginación:** Incrementa el offset en 3 cada vez (3, 6, 9, 12...)
5. **Guía médica:** Úsala solo para preguntas sobre QUÉ HACER, no para buscar especialistas

**Ejemplos de conversación correcta:**

```
Usuario: "Necesito ayuda con depresión, algo barato"
Agente: [Llama buscar_especialista con sintoma="depresión", presupuesto="barato"]
Respuesta: "Encontré 3 especialistas económicos para depresión. Te recomiendo a..."

Usuario: "¿Tienes más opciones?"
Agente: [Llama mas_especialistas con sintoma="depresión", presupuesto="barato", offset=3]
Respuesta: "Aquí tienes 3 especialistas más: ..."

Usuario: "Dame otros"
Agente: [Llama mas_especialistas con sintoma="depresión", presupuesto="barato", offset=6]
Respuesta: "Aquí tienes otras opciones: ..."
```

**Ejemplo INCORRECTO (no hagas esto):**

```
Usuario: "Dame más opciones"
Agente: [Solo repite la información anterior sin llamar a mas_especialistas] ❌
```

---

## 🚀 Despliegue

La API ya está desplegada en Render. Para actualizar:

```bash
cd /Users/vania/Documents/ProyectoMasivos/mental-health-rag-recsys
git add .
git commit -m "Agregar endpoint mas_especialistas para paginación"
git push origin main
```

Render detectará automáticamente los cambios y redesplegará.

---

## 📊 Respuesta de la API

Todos los endpoints retornan JSON con esta estructura:

```json
{
  "success": true,
  "respuesta_voz": "Texto natural para que el agente lo lea",
  "parametros": {
    "sintoma": "ansiedad",
    "genero": "mujer",
    "presupuesto": "barato",
    "ubicacion": "Coyoacán"
  },
  "paginacion": {
    "offset_actual": 3,
    "mostrando": 3,
    "total_disponibles": 10,
    "hay_mas": true,
    "siguiente_offset": 6
  },
  "total_resultados": 3,
  "resultados": [
    {
      "nombre": "Dra. María López",
      "tipo_profesional": "Psicóloga",
      "modalidad": "Online",
      "costo": "Desde $500",
      ...
    }
  ]
}
```

El campo `respuesta_voz` está diseñado para que el agente lo lea directamente al usuario.
