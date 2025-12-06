from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import sys
import pyttsx3
from conecta import conectar_base_datos, registrar_usuario, ingresar_usuario, obtener_categorias, guardar_preferencia_defecto, obtener_fuentes_con_preferencias, guardar_preferencia_fuente, obtener_categorias_con_preferencias, guardar_preferencia_categoria, actualiza_feed, filtra_categoria_feed, guardar_preferencias_ubicacion, rescata_clima
from rss_service import procesar_rss
from categoria_normalizer import obtener_mapeos_categoria, agregar_mapeo_categoria, eliminar_mapeo_categoria
from spotify_service import test_spotify_connection, get_show_episodes

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde React

@app.route('/api/fuentes', methods=['GET'])
def get_fuentes():
    """exitosa con Spotify API
    Endpoint para obtener todas las fuentes de la base de datos
    """
    try:
        print("🔍 Intentando obtener fuentes de la base de datos...")
        fuentes = conectar_base_datos()
        print(f"✅ Fuentes obtenidas: {len(fuentes)} registros")
        if len(fuentes) == 0:
            print("⚠️ No se obtuvieron fuentes de la base de datos")
        return jsonify(fuentes), 200
    except Exception as e:
        print(f"❌ Error al obtener fuentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/fuentes_preferencias/<int:id_usuario>', methods=['GET'])
def get_fuentes_preferencias(id_usuario):
    """
    Endpoint para obtener fuentes con preferencias de un usuario específico
    """
    try:
        print(f"🔍 Solicitud de fuentes con preferencias para usuario {id_usuario}")
        fuentes = obtener_fuentes_con_preferencias(id_usuario)
        print(f"✅ Fuentes obtenidas: {len(fuentes)} registros")
        return jsonify(fuentes), 200
    except Exception as e:
        print(f"❌ Error al obtener fuentes con preferencias: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferencias_fuente', methods=['POST'])
def save_preferencia_fuente():
    """
    Endpoint para guardar preferencia de fuente
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_fuente = data.get('id_fuente')
        prioridad = data.get('prioridad')
        preferencia_on_off = data.get('preferencia_fuente_on_off')
        
        if id_usuario is None or id_fuente is None or prioridad is None:
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
            
        print(f"💾 Guardando preferencia: Usuario {id_usuario}, Fuente {id_fuente}, Prioridad {prioridad}, Estado {preferencia_on_off}")
        resultado = guardar_preferencia_fuente(id_usuario, id_fuente, prioridad, preferencia_on_off)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error al guardar preferencia: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categorias_preferencias/<int:id_usuario>', methods=['GET'])
def get_categorias_preferencias(id_usuario):
    """
    Endpoint para obtener categorías con preferencias de un usuario específico
    """
    try:
        print(f"🔍 Solicitud de categorías con preferencias para usuario {id_usuario}")
        categorias = obtener_categorias_con_preferencias(id_usuario)
        print(f"✅ Categorías obtenidas: {len(categorias)} registros")
        return jsonify(categorias), 200
    except Exception as e:
        print(f"❌ Error al obtener categorías con preferencias: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferencias_categoria', methods=['POST'])
def save_preferencia_categoria():
    """
    Endpoint para guardar preferencia de categoría
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        id_categoria = data.get('id_categoria')
        orden = data.get('orden')
        preferencia_on_off = data.get('preferencia_categoria_on_off')
        
        if id_usuario is None or id_categoria is None or orden is None:
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
            
        print(f"💾 Guardando preferencia cat: Usuario {id_usuario}, Cat {id_categoria}, Orden {orden}, Estado {preferencia_on_off}")
        resultado = guardar_preferencia_categoria(id_usuario, id_categoria, orden, preferencia_on_off)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error al guardar preferencia categoría: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/preferencias_ubicacion', methods=['POST'])
def save_preferencias_ubicacion():
    """
    Endpoint para guardar preferencias de ubicación
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        ubicaciones = data.get('ubicaciones') # Lista de {id, type}
        
        if id_usuario is None:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
            
        print(f"💾 Guardando ubicaciones para usuario {id_usuario}: {len(ubicaciones) if ubicaciones else 0} items")
        resultado = guardar_preferencias_ubicacion(id_usuario, ubicaciones)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error al guardar preferencias ubicación: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/preferencias_ubicacion/<int:id_usuario>', methods=['GET'])
def get_preferencias_ubicacion(id_usuario):
    """
    Endpoint para obtener preferencias de ubicación guardadas
    """
    try:
        from conecta import obtener_preferencias_ubicacion
        print(f"🔍 Obteniendo ubicaciones guardadas para usuario {id_usuario}")
        resultado = obtener_preferencias_ubicacion(id_usuario)
        return jsonify(resultado), 200
    except Exception as e:
        print(f"❌ Error al obtener preferencias ubicación: {str(e)}")
        return jsonify({'success': False, 'ubicaciones': [], 'message': str(e)}), 500


@app.route('/api/clima/<int:id_usuario>', methods=['GET'])
def get_clima_usuario(id_usuario):
    """
    Endpoint para obtener el clima de las ubicaciones preferidas del usuario
    """
    try:
        from conecta import obtener_clima_ubicaciones_preferidas
        print(f"🌤️ Obteniendo clima para usuario {id_usuario}")
        climas = obtener_clima_ubicaciones_preferidas(id_usuario, limite=2)
        return jsonify(climas), 200
    except Exception as e:
        print(f"❌ Error al obtener clima: {str(e)}")
        return jsonify([]), 500


@app.route('/api/rescata_clima', methods=['POST'])
def rescatar_clima_usuario():
    """
    Endpoint para actualizar datos del clima desde Open-Meteo API
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        
        if not id_usuario:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
        
        print(f"🌤️  Rescatando clima para usuario {id_usuario}...")
        resultado = rescata_clima(id_usuario)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint rescata_clima: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'updated': 0}), 500


@app.route('/api/geografia', methods=['GET'])
def get_geografia():
    """
    Endpoint para obtener la estructura geográfica completa
    """
    try:
        # Importar la función desde test_estructura_geo temporalmente
        # TODO: Mover la función a conecta.py
        import sys
        sys.path.insert(0, '.')
        from test_estructura_geo import obtener_estructura_geografica
        
        print("🌍 Obteniendo estructura geográfica")
        estructura = obtener_estructura_geografica()
        return jsonify(estructura), 200
    except Exception as e:
        print(f"❌ Error al obtener geografía: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'id': 'error', 'label': 'Error cargando datos', 'type': 'error', 'children': []}), 500




@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    """
    Endpoint para obtener todas las categorías de la base de datos
    """
    try:
        print("🔍 Intentando obtener categorías de la base de datos...")
        categorias = obtener_categorias()
        print(f"✅ Categorías obtenidas: {len(categorias)} registros")
        return jsonify(categorias), 200
    except Exception as e:
        print(f"❌ Error al obtener categorías: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/categorias/mapeos', methods=['GET'])
def get_categoria_mapeos():
    """
    Endpoint para obtener todos los mapeos de categorías
    """
    try:
        print("🔍 Obteniendo mapeos de categorías...")
        mapeos = obtener_mapeos_categoria()
        print(f"✅ Mapeos obtenidos: {len(mapeos)} registros")
        return jsonify(mapeos), 200
    except Exception as e:
        print(f"❌ Error al obtener mapeos de categorías: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/categorias/mapeos', methods=['POST'])
def create_categoria_mapeo():
    """
    Endpoint para crear un nuevo mapeo de categoría
    """
    try:
        data = request.get_json()
        nombre_alternativo = data.get('nombre_alternativo')
        id_categoria_real = data.get('id_categoria_real')

        if not nombre_alternativo or not id_categoria_real:
            return jsonify({'success': False, 'message': 'Nombre alternativo e ID de categoría real son requeridos'}), 400

        print(f"➕ Creando mapeo: '{nombre_alternativo}' -> ID {id_categoria_real}")
        resultado = agregar_mapeo_categoria(nombre_alternativo, id_categoria_real)

        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400

    except Exception as e:
        print(f"❌ Error al crear mapeo de categoría: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categorias/mapeos/<int:id_mapeo>', methods=['DELETE'])
def delete_categoria_mapeo(id_mapeo):
    """
    Endpoint para eliminar un mapeo de categoría
    """
    try:
        print(f"🗑️ Eliminando mapeo ID: {id_mapeo}")
        resultado = eliminar_mapeo_categoria(id_mapeo)

        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404

    except Exception as e:
        print(f"❌ Error al eliminar mapeo de categoría: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/registro', methods=['POST'])
def registro():
    """
    Endpoint para registrar un nuevo usuario
    """
    try:
        data = request.get_json()
        print(f"🔍 Solicitud de registro recibida: {data.get('email', 'sin email')}")
        
        nombre = data.get('nombre')
        email = data.get('email')
        password = data.get('password')
        direccion = data.get('direccion')
        
        # Validar campos requeridos
        if not nombre or not email or not password:
            return jsonify({'success': False, 'message': 'Nombre, email y contraseña son requeridos'}), 400
        
        resultado = registrar_usuario(nombre, email, password, direccion)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        print(f"❌ Error en endpoint de registro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/ingreso', methods=['POST'])
def ingreso():
    """
    Endpoint para validar credenciales de usuario
    """
    try:
        data = request.get_json()
        print(f"🔍 Solicitud de ingreso recibida: {data.get('email', 'sin email')}")
        
        email = data.get('email')
        password = data.get('password')
        
        # Validar campos requeridos
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email y contraseña son requeridos'}), 400
        
        resultado = ingresar_usuario(email, password)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 401
            
    except Exception as e:
        print(f"❌ Error en endpoint de ingreso: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/admin-panel', methods=['POST'])
def admin_panel():
    """
    Endpoint para ejecutar el panel de control
    """
    try:
        print("🚀 Solicitud para iniciar panel de control")
        panel_path = r"C:\Users\carlo\Documents\Personal\Negocios\Servicio de Noticias\Panel _admin"
        
        if not os.path.exists(panel_path):
            return jsonify({'success': False, 'message': f'No se encuentra la ruta: {panel_path}'}), 404
            
        # Buscar archivo principal
        files = os.listdir(panel_path)
        print(f"📂 Archivos en {panel_path}: {files}")
        
        target_file = None
        candidates = ['main.py', 'app.py', 'panel.py', 'gui.py', 'index.py', 'run.py']
        
        for candidate in candidates:
            if candidate in files:
                target_file = os.path.join(panel_path, candidate)
                break
                
        if not target_file:
            # Intentar buscar cualquier .py si no hay candidatos obvios
            py_files = [f for f in files if f.endswith('.py')]
            if py_files:
                target_file = os.path.join(panel_path, py_files[0])
                
        if target_file:
            print(f"✅ Ejecutando archivo: {target_file}")
            # Ejecutar en segundo plano
            subprocess.Popen([sys.executable, target_file], cwd=panel_path, shell=True)
            return jsonify({'success': True, 'message': f'Panel iniciado ({os.path.basename(target_file)})'}), 200
        else:
            return jsonify({'success': False, 'message': f'No se encontró archivo ejecutable .py en {panel_path}'}), 404
            
    except Exception as e:
        print(f"❌ Error al iniciar panel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/preferencias/default', methods=['POST'])
def set_default_preference():
    """
    Endpoint para establecer preferencias por defecto
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        
        if not id_usuario:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
            
        print(f"⚙️ Estableciendo preferencia por defecto para usuario {id_usuario}")
        resultado = guardar_preferencia_defecto(id_usuario)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint default preferences: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/actualiza_feed', methods=['POST'])
def actualizar_feed_usuario():
    """
    Endpoint para actualizar el feed del usuario basado en sus preferencias actuales
    """
    try:
        data = request.get_json()
        id_usuario = data.get('id_usuario')
        
        if not id_usuario:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
            
        print(f"🔄 Actualizando feed para usuario {id_usuario}")
        resultado = actualiza_feed(id_usuario)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint actualiza_feed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/servicios/lee_rss', methods=['POST'])
def trigger_lee_rss():
    """
    Endpoint para disparar el proceso de lectura de RSS
    """
    try:
        print("🚀 Iniciando proceso de lectura de RSS desde API...")
        resultado = procesar_rss()
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint lee_rss: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@app.route('/api/feed/<int:id_usuario>', methods=['GET'])
def get_user_feed(id_usuario):
    """
    Endpoint para obtener el feed de noticias de un usuario
    """
    try:
        print(f"🔍 Obteniendo feed para usuario {id_usuario}")
        
        # Obtener parámetro opcional de fuente
        source_id = request.args.get('source_id')
        
        from conecta import obtener_conexion
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)
        
        base_sql = """
            SELECT f.id_noticia, n.titulo, n.imagen_principal_url, n.cuerpo as resumen, n.fecha_hora_publicacion, fu.nombre as nombre_fuente, n.url_original as url
            FROM tbl_feed_usuario f
            INNER JOIN tbl_noticia n ON f.id_noticia = n.id_noticia
            INNER JOIN tbl_fuente fu ON n.id_fuente = fu.id_fuente
            WHERE f.id_usuario = %s
        """
        
        params = [id_usuario]
        
        if source_id:
            print(f"🔍 Filtrando por fuente: {source_id}")
            base_sql += " AND n.id_fuente = %s"
            params.append(source_id)
            
        # base_sql += " ORDER BY n.fecha_hora_publicacion DESC LIMIT 20"
        base_sql += " ORDER BY n.fecha_hora_publicacion DESC"
        cur.execute(base_sql, tuple(params))
        noticias = cur.fetchall()
        
        # Formatear fechas para JSON
        for n in noticias:
            if n['fecha_hora_publicacion']:
                n['fecha_hora_publicacion'] = n['fecha_hora_publicacion'].strftime('%Y-%m-%d %H:%M:%S')
                
        print(f"✅ Feed obtenido: {len(noticias)} noticias")
        
        cur.close()
        conn.close()
        
        return jsonify(noticias), 200

    except Exception as e:
        print(f"❌ Error al obtener feed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/feed/<int:id_usuario>/categoria/<int:id_categoria>', methods=['GET'])
def get_user_feed_by_category(id_usuario, id_categoria):
    """
    Endpoint para obtener el feed de noticias de un usuario filtrado por categoría
    """
    try:
        print(f"🔍 Obteniendo feed filtrado para usuario {id_usuario}, categoría {id_categoria}")

        noticias = filtra_categoria_feed(id_usuario, id_categoria)

        return jsonify(noticias), 200

    except Exception as e:
        print(f"❌ Error al obtener feed filtrado por categoría: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generar_mp3', methods=['POST'])
def generar_mp3():
    """
    Endpoint para generar archivo MP3 desde texto usando pyttsx3
    """
    try:
        data = request.get_json()

        if not data or 'texto' not in data:
            return jsonify({
                'success': False,
                'message': 'Se requiere el campo "texto" en el body de la solicitud'
            }), 400

        texto_a_convertir = data['texto']
        id_noticia = data.get('id_noticia')

        # Generar nombre del archivo de salida
        if id_noticia:
            archivo_salida_mp3 = f"{id_noticia}.mp3"
        else:
            # Si no hay id_noticia, usar timestamp como nombre
            import time
            archivo_salida_mp3 = f"audio_{int(time.time())}.mp3"

        # Inicializar el motor de texto a voz
        engine = pyttsx3.init()

        # Configurar propiedades opcionales del motor (puedes ajustar según necesites)
        # engine.setProperty('rate', 180)  # Velocidad de habla
        # engine.setProperty('volume', 1.0)  # Volumen (0.0 a 1.0)

        # Usar el método 'save_to_file' para guardar en un archivo MP3
        engine.save_to_file(texto_a_convertir, archivo_salida_mp3)

        # Ejecutar y esperar a que el proceso termine
        engine.runAndWait()

        print(f"✅ Audio MP3 generado exitosamente en: {archivo_salida_mp3}")

        return jsonify({
            'success': True,
            'message': 'Audio MP3 generado exitosamente',
            'archivo_mp3': archivo_salida_mp3,
            'ruta_completa': os.path.abspath(archivo_salida_mp3)
        }), 200

    except Exception as e:
        print(f"❌ Error generando MP3: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error generando MP3: {str(e)}'
        }), 500


@app.route('/api/spotify/test', methods=['POST'])
def test_spotify():
    """
    Endpoint para probar la conexión con la API de Spotify
    """
    try:
        print("🎵 Probando conexión con Spotify API...")
        resultado = test_spotify_connection()
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Error en endpoint test_spotify: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@app.route('/api/spotify/episodes/<show_id>', methods=['GET'])
def get_spotify_episodes(show_id):
    """
    Endpoint para obtener episodios de un show de Spotify
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        print(f"🎧 Obteniendo episodios del show {show_id} (límite: {limit})...")
        
        resultado = get_show_episodes(show_id, limit)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404
            
    except Exception as e:
        print(f"❌ Error en endpoint get_spotify_episodes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando servidor Flask")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("📋 Endpoints disponibles:")
    print("   - GET  /api/fuentes")
    print("   - GET  /api/categorias")
    print("   - GET  /api/categorias/mapeos")
    print("   - POST /api/categorias/mapeos")
    print("   - DEL  /api/categorias/mapeos/<id>")
    print("   - GET  /api/feed/<usuario>")
    print("   - GET  /api/feed/<usuario>/categoria/<categoria>")
    print("   - POST /api/registro")
    print("   - POST /api/ingreso")
    print("   - POST /api/generar_mp3")
    print("=" * 60)
    print("\n✨ Servidor corriendo. Presiona Ctrl+C para detener.\n")
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()


