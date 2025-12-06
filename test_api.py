"""
Script para probar que la API Flask responda correctamente
Ejecutar: python test_api.py
"""
import requests
import json

def test_api():
    url = "http://localhost:5000/api/fuentes"
    
    print("=" * 60)
    print("🧪 PRUEBA DE LA API FLASK")
    print("=" * 60)
    print(f"📍 URL: {url}")
    print()
    
    try:
        print("🔍 Enviando solicitud GET a la API...")
        response = requests.get(url, timeout=5)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ¡API funcionando correctamente!")
            print(f"📦 Total de registros recibidos: {len(data)}")
            print()
            
            if len(data) > 0:
                print("📋 Datos recibidos:")
                print("-" * 60)
                for i, fuente in enumerate(data, 1):
                    print(f"{i}. ID: {fuente.get('id_fuente')}")
                    print(f"   Nombre: {fuente.get('nombre')}")
                    print(f"   Descripción: {fuente.get('descripcion')}")
                    print()
            else:
                print("⚠️ La API retornó un array vacío")
        else:
            print(f"❌ Error: La API retornó status code {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar con la API Flask")
        print()
        print("💡 Solución:")
        print("   1. Asegúrate de que la API Flask esté corriendo")
        print("   2. Ejecuta: python api.py")
        print("   3. Verifica que el puerto 5000 esté disponible")
        
    except requests.exceptions.Timeout:
        print("❌ ERROR: La solicitud tardó demasiado (timeout)")
        
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()

