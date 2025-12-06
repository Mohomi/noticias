#!/usr/bin/env python3
"""
Script de prueba para el sistema de mapeo de categorías
"""

from categoria_normalizer import obtener_mapeos_categoria, normalizar_categoria

def test_obtener_mapeos():
    print("🔍 Probando obtener_mapeos_categoria...")
    mapeos = obtener_mapeos_categoria()
    print(f"✅ Encontrados {len(mapeos)} mapeos")

    if mapeos:
        print("📋 Primeros 5 mapeos:")
        for m in mapeos[:5]:
            print(f"  '{m['nombre_alternativo']}' -> '{m['nombre_categoria_real']}'")

def test_normalizar():
    print("\n🔍 Probando normalizar_categoria...")

    # Probar algunos casos
    casos_prueba = ['nacional', 'país', 'internacional', 'mundo', 'categoria_inexistente']

    for caso in casos_prueba:
        id_cat, nombre_cat = normalizar_categoria(caso)
        if id_cat:
            print(f"  ✅ '{caso}' -> '{nombre_cat}' (ID: {id_cat})")
        else:
            print(f"  ⚠️ '{caso}' -> Sin mapeo (usando: '{nombre_cat}')")

if __name__ == "__main__":
    test_obtener_mapeos()
    test_normalizar()
    print("\n🎉 Pruebas completadas!")
