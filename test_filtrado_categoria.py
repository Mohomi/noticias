#!/usr/bin/env python3
"""
Script de prueba para la nueva funcionalidad de filtrado por categorías
"""

from conecta import filtra_categoria_feed

def test_filtrado_categoria():
    print("🔍 Probando filtrado por categoría...")

    # Ejemplo: filtrar noticias del usuario 1 por categoría 5 (Política)
    try:
        noticias = filtra_categoria_feed(1, 5)

        print(f"✅ Encontradas {len(noticias)} noticias en la categoría")

        if noticias:
            print("📋 Primeras 2 noticias:")
            for i, noticia in enumerate(noticias[:2]):
                print(f"  {i+1}. {noticia['titulo'][:50]}...")
                print(f"      Fuente: {noticia['nombre_fuente']}")
                print(f"      Fecha: {noticia['fecha_hora_publicacion']}")
        else:
            print("⚠️ No se encontraron noticias para esta categoría")

    except Exception as e:
        print(f"❌ Error al probar filtrado: {e}")

if __name__ == "__main__":
    test_filtrado_categoria()
    print("\n🎉 Prueba completada!")
