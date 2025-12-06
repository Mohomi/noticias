import requests
import json

def debug_feed():
    # ID de usuario de prueba (asegúrate de que exista en tu BD)
    id_usuario = 1 
    url = f"http://localhost:5000/api/feed/{id_usuario}"
    
    print(f"🔍 Probando endpoint: {url}")
    
    try:
        response = requests.get(url)
        print(f"📡 Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("📦 Response JSON (Type):", type(data))
            print("📦 Response JSON (Content):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if isinstance(data, dict) and 'error' in data:
                print("❌ API retornó un error explícito.")
            elif isinstance(data, list):
                print("✅ API retornó una lista (Correcto).")
            else:
                print("⚠️ API retornó un objeto inesperado.")
                
        except json.JSONDecodeError:
            print("❌ Error decodificando JSON. Response Text:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    debug_feed()
