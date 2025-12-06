import feedparser
import mysql.connector
from datetime import datetime
from bs4 import BeautifulSoup
import re
from conecta import obtener_conexion
from categoria_normalizer import normalizar_categoria

# ID del formato (ej. RSS)
ID_FORMATO = 1 

def limpia_campos(texto_html):
    """
    Limpia el texto HTML eliminando todas las etiquetas HTML, CSS y scripts.
    Retorna texto plano limpio.
    
    Args:
        texto_html: Texto que puede contener HTML, CSS o scripts
        
    Returns:
        str: Texto limpio sin etiquetas HTML
    """
    if not texto_html or not isinstance(texto_html, str):
        return ''
    
    try:
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(texto_html, 'html.parser')
        
        # Eliminar tags de script y style completamente
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        # Obtener el texto limpio
        texto_limpio = soup.get_text()
        
        # Limpiar espacios en blanco excesivos
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        
        return texto_limpio
        
    except Exception as e:
        print(f"⚠️ Error limpiando campo: {e}")
        # Si falla BeautifulSoup, intentar limpieza básica con regex
        texto_limpio = re.sub(r'<[^>]+>', '', texto_html)
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        return texto_limpio


def procesar_rss():
    """
    Función principal para procesar los feeds RSS de las fuentes activas.
    Retorna un diccionario con el resumen del proceso.
    """
    conn = None
    cur = None
    resumen = {
        'fuentes_procesadas': 0,
        'noticias_insertadas': 0,
        'errores': []
    }

    try:
        # Conectar a la base de datos usando la función centralizada
        conn = obtener_conexion()
        cur = conn.cursor()
        print("✅ rss_service: Conexión a la base de datos MySQL exitosa.")

        # 1. Obtener las fuentes que tienen RSS activo
        print("🔍 rss_service: Buscando fuentes con RSS activo...")
        cur.execute("SELECT id_fuente, link_rss, nombre FROM tbl_fuente WHERE tiene_rss = 1")
        fuentes = cur.fetchall()

        if not fuentes:
            print("⚠️ rss_service: No se encontraron fuentes con RSS activo.")
            return {'success': True, 'message': 'No hay fuentes con RSS activo', 'data': resumen}
        
        for fuente in fuentes:
            id_fuente_actual = fuente[0]
            url_rss_actual = fuente[1]
            nombre_fuente = fuente[2]
            
            print(f"Procesando fuente: {nombre_fuente}. Presiona Enter para continuar...")
            input()

            if not url_rss_actual:
                print(f"⚠️ rss_service: La fuente '{nombre_fuente}' (ID: {id_fuente_actual}) tiene RSS activo pero no tiene URL definida. Saltando.")
                continue

            print(f"\n--- Procesando fuente: {nombre_fuente} (ID: {id_fuente_actual}) ---")
            print(f"URL: {url_rss_actual}")
            resumen['fuentes_procesadas'] += 1

            # Parsear el RSS
            try:
                feed = feedparser.parse(url_rss_actual)
                
                if feed.bozo:
                    print(f"⚠️ rss_service: Advertencia parseando feed de {nombre_fuente}: {feed.bozo_exception}")

                contador_noticias_fuente = 0
                
                # Mostrar los títulos de los artículos e insertar en BD
                for entry in feed.entries:
                    # Extraer datos básicos y limpiar HTML
                    titulo = limpia_campos(entry.title)
                    cuerpo = limpia_campos(getattr(entry, 'summary', '')) # Usamos summary como cuerpo por ahora
                    
                    # Intentar obtener la fecha
                    try:
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            fecha_dt = datetime(*entry.published_parsed[:6])
                            fecha_publicacion = fecha_dt.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    autor = getattr(entry, 'author', 'Desconocido')
                    url_original = entry.link
                    
                    # Intentar buscar una imagen
                    imagen_url = None

                    # Para la fuente específica id_fuente=5, buscar en df:foto600
                    if id_fuente_actual == 5:
                        foto600 = getattr(entry, 'df:foto600', None)
                        if foto600:
                            imagen_url = f"https://www.df.cl{foto600}"
                    else:
                        # Para otras fuentes, buscar en links
                        if 'links' in entry:
                            for link in entry.links:
                                if link.get('type', '').startswith('image'):
                                    imagen_url = link['href']
                                    break
                    
                    # Insertar en la base de datos (MySQL)
                    # Usamos INSERT IGNORE para evitar duplicados basados en url_original (asumiendo que es UNIQUE o PK)
                    # Si no hay constraint UNIQUE en url_original, esto insertará duplicados.
                    # Idealmente debería haber un UNIQUE INDEX en url_original.
                    
                    # Primero verificamos si ya existe para no duplicar (si no hay unique constraint)
                    cur.execute("SELECT id_noticia FROM tbl_noticia WHERE url_original = %s", (url_original,))
                    existe_noticia = cur.fetchone()
                    
                    id_noticia = None
                    
                    if existe_noticia:
                        # print(f"  -> Noticia ya existe: {titulo[:30]}...")
                        id_noticia = existe_noticia[0]
                    else:
                        sql = """
                            INSERT INTO tbl_noticia 
                            (titulo, cuerpo, fecha_hora_publicacion, autor, url_original, imagen_principal_url, id_fuente, id_formato)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(sql, (titulo, cuerpo, fecha_publicacion, autor, url_original, imagen_url, id_fuente_actual, ID_FORMATO))
                        id_noticia = cur.lastrowid
                        contador_noticias_fuente += 1
                        resumen['noticias_insertadas'] += 1
                    
                    # --- PROCESAMIENTO DE CATEGORÍAS ---
                    # Buscar etiquetas/categorías en el feed
                    categorias_encontradas = []
                    ids_categorias_validas = [] # Para guardar IDs de categorías reales (no de tbl_otra_categoria)
                    
                    # 1. Buscar en 'tags' (común en feedparser)
                    if hasattr(entry, 'tags'):
                        for tag in entry.tags:
                            if hasattr(tag, 'term') and tag.term:
                                categorias_encontradas.append(tag.term)
                    
                    # 3. Buscar en 'keywords' (User request)
                    if hasattr(entry, 'keywords') and entry.keywords:
                        if isinstance(entry.keywords, list):
                             categorias_encontradas.extend(entry.keywords)
                        else:
                             categorias_encontradas.append(str(entry.keywords))

                    # Procesar cada categoría encontrada
                    # print(f"    🔍 Categorías encontradas (raw): {categorias_encontradas}")
                    
                    for cat_raw in categorias_encontradas:
                        if not isinstance(cat_raw, str):
                            continue

                        nombre_categoria = cat_raw.strip()
                        print(f"    👉 Procesando categoría: '{nombre_categoria}'", flush=True)

                        if not nombre_categoria:
                            continue

                        # PRIMERO: Verificar si la categoría existe tal cual en tbl_categoria
                        cur.execute("SELECT id_categoria FROM tbl_categoria WHERE nombre = %s", (nombre_categoria,))
                        cat_existente = cur.fetchone()

                        id_categoria = None

                        if cat_existente:
                            id_categoria = cat_existente[0]
                            ids_categorias_validas.append(id_categoria) # Guardamos ID válido
                            print(f"    ✅ Categoría encontrada: '{nombre_categoria}'")
                            continue

                        # SEGUNDO: Si no existe tal cual, intentar normalizar la categoría usando el mapeo
                        id_categoria_normalizada, nombre_normalizado = normalizar_categoria(nombre_categoria)

                        if id_categoria_normalizada:
                            # ¡Éxito! La categoría fue mapeada a una existente
                            # Categoria Normalizada y mapeada
                            # print(f"    ✅ Categoría normalizada: '{nombre_categoria}' -> '{nombre_normalizado}'")
                            ids_categorias_validas.append(id_categoria_normalizada)
                            continue

                        # TERCERO: Si no se mapea, crear registro en tbl_otra_categoria
                            # Si no existe, crear registro en tbl_otra_categoria
                            try:
                                # Asegurar que la tabla existe (Idempotente)
                                cur.execute("""
                                    CREATE TABLE IF NOT EXISTS tbl_otra_categoria (
                                        id_categoria SERIAL PRIMARY KEY,
                                        nombre VARCHAR(100) NOT NULL,
                                        id_fuente INTEGER NOT NULL,
                                        id_noticia INTEGER NOT NULL,
                                        UNIQUE KEY unique_categoria_fuente (nombre, id_fuente)
                                    )
                                """)

                                # Verificar si ya existe la categoría para esta fuente
                                cur.execute("SELECT id_categoria FROM tbl_otra_categoria WHERE nombre = %s AND id_fuente = %s", (nombre_categoria, id_fuente_actual))
                                cat_otra_existente = cur.fetchone()

                                if not cat_otra_existente:
                                    # Insertar la categoría con nombre, id_fuente e id_noticia
                                    cur.execute("INSERT INTO tbl_otra_categoria (nombre, id_fuente, id_noticia) VALUES (%s, %s, %s)", (nombre_categoria, id_fuente_actual, id_noticia))
                                    print(f"    ⚠️ Nueva categoría en tbl_otra_categoria: '{nombre_categoria}' (fuente ID: {id_fuente_actual}, noticia ID: {id_noticia})")
                                else:
                                    print(f"    ℹ️ Categoría '{nombre_categoria}' ya existía en tbl_otra_categoria para esta fuente")

                                # IMPORTANTE: No vinculamos con tbl_noticia_categoria porque el ID generado
                                # pertenece a tbl_otra_categoria y no a tbl_categoria.
                                # Para futura implementación, aquí iría el código de vinculación:
                                #
                                # # Vincular con tbl_noticia_categoria usando el ID de tbl_otra_categoria
                                # id_categoria_otra = cur.lastrowid if not cat_otra_existente else cat_otra_existente[0]
                                # try:
                                #     sql_rel_otra = """
                                #         INSERT IGNORE INTO tbl_noticia_categoria (id_noticia, id_categoria)
                                #         VALUES (%s, %s)
                                #     """
                                #     cur.execute(sql_rel_otra, (id_noticia, id_categoria_otra))
                                #     print(f"    🔗 Vinculada noticia con categoría de tbl_otra_categoria: {id_categoria_otra}")
                                # except mysql.connector.Error as err_rel_otra:
                                #     print(f"    ❌ Error vinculando noticia-categoría (tbl_otra_categoria): {err_rel_otra}")
                                #
                                id_categoria = None
                            except mysql.connector.Error as err_cat:
                                print(f"    ❌ Error creando categoría '{nombre_categoria}' en tbl_otra_categoria: {err_cat}")
                                continue

                        # Vincular noticia con categoría en tbl_noticia_categoria
                        if id_noticia and id_categoria:
                            try:
                                sql_rel = """
                                    INSERT IGNORE INTO tbl_noticia_categoria (id_noticia, id_categoria)
                                    VALUES (%s, %s)
                                """
                                cur.execute(sql_rel, (id_noticia, id_categoria))
                            except mysql.connector.Error as err_rel:
                                print(f"    ❌ Error vinculando noticia-categoría: {err_rel}")

                    if not categorias_encontradas:
                        print(f"    ⚠️ No se encontraron categorías para la noticia: '{titulo[:30]}...'")
                        # Debug: ver qué tiene el entry
                        # print(f"    Keys disponibles: {entry.keys()}")

                    # --- POPULAR TBL_FEED_USUARIO ---
                    # Insertar registro para usuarios que siguen la fuente O la categoría
                    if id_noticia:
                        try:
                            # Asegurar que la tabla existe
                            cur.execute("""
                                CREATE TABLE IF NOT EXISTS tbl_feed_usuario (
                                    id_feed_usuario SERIAL PRIMARY KEY,
                                    id_usuario INTEGER NOT NULL,
                                    id_noticia INTEGER NOT NULL,
                                    leido BOOLEAN DEFAULT FALSE,
                                    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    UNIQUE KEY unique_user_news (id_usuario, id_noticia)
                                )
                            """)

                            # Query para encontrar usuarios interesados
                            # 1. Usuarios que siguen la fuente
                            sql_feed_fuente = """
                                INSERT IGNORE INTO tbl_feed_usuario (id_usuario, id_noticia)
                                SELECT DISTINCT id_usuario, %s 
                                FROM tbl_preferenciafuente 
                                WHERE id_fuente = %s AND preferencia_fuente_on_off = 1
                            """
                            cur.execute(sql_feed_fuente, (id_noticia, id_fuente_actual))
                            
                            # 2. Usuarios que siguen alguna de las categorías encontradas
                            if ids_categorias_validas:
                                # Crear placeholders para la lista de IDs: %s, %s, %s...
                                placeholders = ', '.join(['%s'] * len(ids_categorias_validas))
                                sql_feed_cat = f"""
                                    INSERT IGNORE INTO tbl_feed_usuario (id_usuario, id_noticia)
                                    SELECT DISTINCT id_usuario, %s 
                                    FROM tbl_preferenciacategoria 
                                    WHERE id_categoria IN ({placeholders}) AND preferencia_categoria_on_off = 1
                                """
                                # Parametros: id_noticia + lista de ids de categorias
                                params = [id_noticia] + ids_categorias_validas
                                cur.execute(sql_feed_cat, params)
                            
                        except mysql.connector.Error as err_feed:
                            print(f"    ❌ Error actualizando feed de usuarios: {err_feed}")

                print(f"  -> Se insertaron {contador_noticias_fuente} nuevas noticias de '{nombre_fuente}'.")
                conn.commit()

            except Exception as e_feed:
                msg = f"Error procesando el feed de '{nombre_fuente}': {str(e_feed)}"
                print(f"❌ {msg}")
                resumen['errores'].append(msg)

        print("\n✅ rss_service: Proceso global finalizado exitosamente.")
        return {'success': True, 'message': 'Proceso RSS finalizado', 'data': resumen}

    except mysql.connector.Error as err:
        msg = f"Error de conexión o consulta MySQL: {err}"
        print(f"❌ {msg}")
        return {'success': False, 'message': msg}
    except Exception as e:
        msg = f"Ocurrió un error general: {str(e)}"
        print(f"❌ {msg}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': msg}
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
