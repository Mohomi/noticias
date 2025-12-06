#!/usr/bin/env python3
"""
Script de diagnóstico para la aplicación React + Flask
"""

import requests
import time
import subprocess
import sys

def check_flask_server():
    """Verificar que el servidor Flask esté corriendo"""
    print("🔍 Verificando servidor Flask...")

    try:
        response = requests.get("http://127.0.0.1:5000/api/fuentes", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor Flask corriendo en puerto 5000")
            return True
        else:
            print(f"❌ Servidor Flask responde con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor Flask no está corriendo en puerto 5000")
        print("   💡 Ejecuta: python api.py")
        return False
    except Exception as e:
        print(f"❌ Error conectando con Flask: {e}")
        return False

def check_vite_server():
    """Verificar que el servidor Vite esté corriendo"""
    print("\n🔍 Verificando servidor Vite/React...")

    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor Vite corriendo en puerto 3000")
            return True
        else:
            print(f"❌ Servidor Vite responde con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor Vite no está corriendo en puerto 3000")
        print("   💡 Ejecuta: npm run dev")
        return False
    except Exception as e:
        print(f"❌ Error conectando con Vite: {e}")
        return False

def test_api_endpoints():
    """Probar algunos endpoints de la API"""
    print("\n🔍 Probando endpoints de la API...")

    endpoints = [
        "/api/fuentes",
        "/api/categorias",
    ]

    for endpoint in endpoints:
        try:
            url = f"http://127.0.0.1:5000{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: Código {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def check_frontend_dependencies():
    """Verificar dependencias del frontend"""
    print("\n🔍 Verificando dependencias del frontend...")

    try:
        # Verificar si existe package.json
        with open("package.json", "r") as f:
            import json
            package = json.load(f)
            print(f"✅ package.json encontrado - {len(package.get('dependencies', {}))} dependencias")

        # Verificar si existe node_modules
        import os
        if os.path.exists("node_modules"):
            print("✅ node_modules existe")
        else:
            print("❌ node_modules no existe - ejecuta: npm install")

    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")

def main():
    print("🚀 Diagnóstico de la aplicación NotiStream")
    print("=" * 50)

    # Verificar servidores
    flask_ok = check_flask_server()
    vite_ok = check_vite_server()

    # Si ambos servidores están corriendo, probar API
    if flask_ok:
        test_api_endpoints()

    # Verificar dependencias
    check_frontend_dependencies()

    print("\n" + "=" * 50)
    print("📋 Resumen:")

    if flask_ok and vite_ok:
        print("✅ Ambos servidores están corriendo correctamente")
        print("🌐 Accede a: http://localhost:3000")
    else:
        print("❌ Hay problemas con los servidores")

        if not flask_ok:
            print("   - Servidor Flask: NO CORRIENDO")
            print("   - Solución: python api.py")

        if not vite_ok:
            print("   - Servidor Vite: NO CORRIENDO")
            print("   - Solución: npm run dev")

    print("\n💡 Si aún no funciona:")
    print("   1. Abre la consola del navegador (F12)")
    print("   2. Busca errores en la pestaña Console")
    print("   3. Verifica que no haya errores de CORS")

if __name__ == "__main__":
    main()
