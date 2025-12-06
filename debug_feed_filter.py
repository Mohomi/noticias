import requests
import json

def debug_feed_filter():
    # ID de usuario y fuente reportados en el error
    id_usuario = 3
    source_id = 4
    url = f"http://localhost:5000/api/feed/{id_usuario}?source_id={source_id}"
    
    print(f"🔍 Probando endpoint: {url}")
    
    try:
        response = requests.get(url)
        print(f"📡 Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("📦 Response JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("❌ Error decodificando JSON. Response Text:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    debug_feed_filter()
