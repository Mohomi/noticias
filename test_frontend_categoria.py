#!/usr/bin/env python3
"""
Script para probar el filtrado por categoría desde el frontend
"""

import requests

def test_categoria_filter():
    print("🔍 Probando filtrado por categoría...")

    # ID de usuario de prueba (cambiar según tu base de datos)
    user_id = 1
    # ID de categoría de prueba (cambiar según tu base de datos, ej: 5 para Política)
    categoria_id = 5

    try:
        # Probar el endpoint de filtrado por categoría
        url = f"http://localhost:5000/api/feed/{user_id}/categoria/{categoria_id}"
        print(f"📡 Probando URL: {url}")

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint funciona! Recibidas {len(data)} noticias")

            if data:
                print("📋 Primera noticia:")
                noticia = data[0]
                print(f"  - Título: {noticia.get('titulo', 'N/A')[:50]}...")
                print(f"  - Fuente: {noticia.get('nombre_fuente', 'N/A')}")
                print(f"  - Fecha: {noticia.get('fecha_hora_publicacion', 'N/A')}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_categoria_filter()
