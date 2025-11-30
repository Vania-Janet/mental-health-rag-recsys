#!/usr/bin/env python3
"""
Script para REGENERAR el índice FAISS con los datos actualizados
Ejecutar cuando se actualiza recursos_salud_mental_cdmx.json
"""

import os
import shutil
from retrieval_system import MentalHealthRetrieval

# Eliminar cache viejo
cache_dir = 'faiss_recursos'
if os.path.exists(cache_dir):
    print(f"🗑️  Eliminando cache viejo: {cache_dir}")
    shutil.rmtree(cache_dir)
    print("✓ Cache eliminado")

# Regenerar índice con force_rebuild=True
print("\n🔄 Regenerando índice FAISS con datos actualizados...")
print("⏳ Esto tomará unos minutos (generando embeddings con OpenAI)...\n")

retrieval_system = MentalHealthRetrieval(
    'recursos_salud_mental_cdmx.json',
    force_rebuild=True  # Forzar regeneración
)

print("\n" + "="*70)
print("✅ ÍNDICE FAISS REGENERADO EXITOSAMENTE")
print("="*70)
print(f"Total de recursos indexados: {len(retrieval_system.especialistas)}")

# Verificar psicólogos
psicologos = [e for e in retrieval_system.especialistas if 'psicólog' in e.get('tipo_profesional', '').lower()]
print(f"Psicólogos encontrados: {len(psicologos)}")

psiquiatras = [e for e in retrieval_system.especialistas if 'psiquiatra' in e.get('tipo_profesional', '').lower()]
print(f"Psiquiatras encontrados: {len(psiquiatras)}")

print("\n🎉 Ahora el sistema está listo para usar con todos los datos actualizados")
