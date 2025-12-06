#!/usr/bin/env python3
"""
Script para comparar el feed normal vs filtrado por categoría
"""

import requests

def comparar_filtros():
    print("🔍 Comparando filtros de feed...")

    user_id = 1
    categoria_id = 5  # Política

    try:
        # Feed completo
        url_completo = f"http://localhost:5000/api/feed/{user_id}"
        print(f"📡 Feed completo: {url_completo}")

        response_completo = requests.get(url_completo)
        if response_completo.status_code == 200:
            data_completo = response_completo.json()
            print(f"✅ Feed completo: {len(data_completo)} noticias")
        else:
            print(f"❌ Error en feed completo: {response_completo.status_code}")
            return

        # Feed filtrado por categoría
        url_filtrado = f"http://localhost:5000/api/feed/{user_id}/categoria/{categoria_id}"
        print(f"📡 Feed filtrado: {url_filtrado}")

        response_filtrado = requests.get(url_filtrado)
        if response_filtrado.status_code == 200:
            data_filtrado = response_filtrado.json()
            print(f"✅ Feed filtrado: {len(data_filtrado)} noticias de categoría {categoria_id}")
        else:
            print(f"❌ Error en feed filtrado: {response_filtrado.status_code}")
            return

        # Comparación
        print("\n📊 Comparación:")
        print(f"  - Feed completo: {len(data_completo)} noticias")
        print(f"  - Feed filtrado: {len(data_filtrado)} noticias")
        if len(data_completo) > 0:
            proporcion = len(data_filtrado) / len(data_completo) * 100
            print(f"  - Proporción: {proporcion:.1f}%")
        else:
            print("  - Proporción: N/A (feed completo vacío)")

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    comparar_filtros()
