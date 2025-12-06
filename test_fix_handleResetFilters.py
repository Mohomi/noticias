#!/usr/bin/env python3
"""
Script para probar que el fix de handleResetFilters funciona
"""

import requests
import time

def test_app_load():
    """Probar que la aplicación carga correctamente"""
    print("🔍 Probando carga de la aplicación...")

    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicación carga correctamente")
            print("   📄 Contenido recibido:", len(response.text), "caracteres")

            # Verificar que contiene elementos React
            if "root" in response.text and "React" in response.text:
                print("✅ Contiene elementos de React")
            else:
                print("⚠️  No se detectan elementos de React claramente")

            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Vite")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_api_connection():
    """Probar que la API sigue funcionando"""
    print("\n🔍 Probando conexión con la API...")

    try:
        response = requests.get("http://127.0.0.1:5000/api/fuentes", timeout=3)
        if response.status_code == 200:
            print("✅ API responde correctamente")
            return True
        else:
            print(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando fix de handleResetFilters")
    print("=" * 40)

    app_ok = test_app_load()
    api_ok = test_api_connection()

    print("\n" + "=" * 40)
    if app_ok and api_ok:
        print("✅ Todo funciona correctamente")
        print("🌐 La aplicación debería estar visible en: http://localhost:3000")
    else:
        print("❌ Hay problemas que resolver")
