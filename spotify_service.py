"""
Servicio para interactuar con la API de Spotify.
"""
import requests
import base64



# Credenciales de Spotify (constantes del módulo)
CLIENT_ID = "fed6bc75bb35424ca36951e8a0876287"
CLIENT_SECRET = "79a3ae5a84de45aabc7a583c6cb3d434"


def get_access_token():
    """
    Obtiene un access token de Spotify usando Client Credentials Flow.
    
    Returns:
        str or None: Access token si es exitoso, None si falla
    """
    try:
        auth_url = "https://accounts.spotify.com/api/token"
        
        # Codificar credenciales en Base64
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(auth_url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            print(f"❌ Error obteniendo token: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en get_access_token: {str(e)}")
        return None


def test_spotify_connection():
    """
    Prueba la conexión con la API de Spotify usando las credenciales proporcionadas.
    
    Returns:
        dict: Resultado de la prueba con 'success' y 'message'
    """
    try:
        print("🎵 Intentando conectar con Spotify API...")
        
        # Usar la función auxiliar para obtener el token
        access_token = get_access_token()
        
        if access_token:
            print("✅ Conexión exitosa con Spotify API")
            return {
                'success': True,
                'message': '✅ Conexión exitosa con Spotify API',
                'access_token': access_token[:20] + '...',
                'token_type': 'Bearer',
                'expires_in': 3600
            }
        else:
            return {
                'success': False,
                'message': '❌ No se pudo obtener el token de acceso'
            }
            
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con Spotify")
        return {
            'success': False,
            'message': '❌ Timeout: No se pudo conectar con Spotify en el tiempo esperado'
        }
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con Spotify")
        return {
            'success': False,
            'message': '❌ Error de conexión: Verifique su conexión a Internet'
        }
    except Exception as e:
        print(f"❌ Error inesperado al conectar con Spotify: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'❌ Error inesperado: {str(e)}'
        }


def get_show_episodes(show_id, limit=10):
    """
    Obtiene los episodios de un show de Spotify.
    
    Args:
        show_id: ID del show de Spotify
        limit: Número máximo de episodios a obtener (default: 10)
        
    Returns:
        dict: Resultado con 'success' y 'episodes' o 'message' de error
    """
    try:
        print(f"🎧 Obteniendo episodios del show {show_id}...")
        
        # Obtener token de acceso
        access_token = get_access_token()
        
        if not access_token:
            return {
                'success': False,
                'message': '❌ No se pudo obtener el token de acceso'
            }
        
        # Endpoint para obtener episodios del show
        episodes_url = f"https://api.spotify.com/v1/shows/{show_id}/episodes"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "limit": limit,
            "market": "US"  # Mercado requerido para algunos shows
        }
        
        response = requests.get(episodes_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            for item in data.get('items', []):
                episodes.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'description': item.get('description', '')[:200] + '...' if len(item.get('description', '')) > 200 else item.get('description', ''),
                    'release_date': item.get('release_date'),
                    'duration_ms': item.get('duration_ms'),
                    'duration_min': round(item.get('duration_ms', 0) / 60000, 1),
                    'external_url': item.get('external_urls', {}).get('spotify', '')
                })
            
            print(f"✅ Obtenidos {len(episodes)} episodios")
            return {
                'success': True,
                'episodes': episodes,
                'total': data.get('total', 0)
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'message': f'❌ Show no encontrado (ID: {show_id})'
            }
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"❌ Error obteniendo episodios: {error_msg}")
            return {
                'success': False,
                'message': f'❌ Error al obtener episodios: {error_msg}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': '❌ Timeout al obtener episodios de Spotify'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': '❌ Error de conexión al obtener episodios'
        }
    except Exception as e:
        print(f"❌ Error inesperado en get_show_episodes: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'❌ Error inesperado: {str(e)}'
        }


if __name__ == "__main__":
    # Prueba directa del servicio
    print("=" * 60)
    print("🎵 Probando conexión con Spotify API")
    print("=" * 60)
    resultado = test_spotify_connection()
    print(f"\nResultado: {resultado}")
