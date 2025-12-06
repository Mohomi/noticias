import requests
import json

def test_rescata_clima_endpoint():
    print("🧪 Testeando endpoint /api/rescata_clima...")
    
    # ID de usuario de prueba (asegúrate de que exista y tenga ubicaciones preferidas)
    # Si no sabes un ID, puedes intentar con 1 o buscar uno en la BD
    id_usuario = 1 
    
    url = "http://localhost:5000/api/rescata_clima"
    payload = {"id_usuario": id_usuario}
    headers = {"Content-Type": "application/json"}
    
    try:
        print(f"  Enviando POST a {url} con payload {payload}")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Test Exitoso: El endpoint respondió success=True")
                print(f"   Mensaje: {data.get('message')}")
                print(f"   Ubicaciones actualizadas: {data.get('updated')}")
            else:
                print("⚠️  Test Fallido: El endpoint respondió success=False")
        else:
            print("❌ Test Fallido: Status code no es 200")
            
    except Exception as e:
        print(f"❌ Error conectando al endpoint: {e}")

if __name__ == "__main__":
    test_rescata_clima_endpoint()
