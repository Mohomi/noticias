import requests

def probar_clima():
    id_usuario = 1
    url = f"http://localhost:5000/api/clima/{id_usuario}"
    
    print(f"🔍 Probando endpoint: {url}")
    
    try:
        response = requests.get(url)
        print(f"📡 Status Code: {response.status_code}")
        
        data = response.json()
        print("📦 Response JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import json
    probar_clima()
