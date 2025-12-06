import os
import mysql.connector
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo 'connect.env'
# Asegúrate de tener el archivo connect.env en el mismo directorio
load_dotenv('connect.env')

def obtener_conexion():
    """
    Obtiene una conexión a la base de datos MySQL.
    Retorna el objeto de conexión.
    """
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '3306'))
    usuario = os.getenv('DB_USER', 'root')
    contrasena = os.getenv('DB_PASSWORD', '')
    base_datos = os.getenv('DB_NAME', 'noti_stream')  # Usar noti_stream como especificado
    
    try:
        conexion = mysql.connector.connect(
            host=host,
            port=port,
            user=usuario,
            password=contrasena,
            database=base_datos
        )
        return conexion
    except mysql.connector.Error as error:
        print(f"❌ Error al conectar a MySQL: {error}")
        raise error

def conectar_base_datos():
    """
    Establece una conexión a la base de datos MySQL utilizando
    parámetros definidos en variables de entorno.
    Retorna una lista de diccionarios con los datos de tbl_fuente.
    """
    # Definir los parámetros de conexión recuperados del entorno.
    # Se usan los valores solicitados como defaults, pero se prioriza el archivo .env
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '3306'))
    usuario = os.getenv('DB_USER', 'root')
    contrasena = os.getenv('DB_PASSWORD', '')
    base_datos = os.getenv('DB_NAME', 'noti')
    
    print(f"🔗 Conectando a MySQL: {host}:{port}, base de datos: {base_datos}, usuario: {usuario}")

    conexion = None
    resultados = []
    cursor = None
    try:
        # Intentar conectar a la base de datos usando el conector oficial
        conexion = mysql.connector.connect(
            host=host,
            port=port,
            user=usuario,
            password=contrasena,
            database=base_datos
        )

        if conexion.is_connected():
            print("✅ Conexión establecida con MySQL")
            # Crear un cursor para ejecutar una consulta de prueba
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT DATABASE();")
            registro = cursor.fetchone()
            print(f"📊 Base de datos conectada: {registro}")
            
            # lectura de BDD tabla fuentes
            select_query = "SELECT * FROM tbl_fuente;"
            print(f"🔍 Ejecutando consulta: {select_query}")
            cursor.execute(select_query)
            resultados = cursor.fetchall()
            print(f"📦 Resultados obtenidos: {len(resultados)} registros")
               
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
                print("🔌 Conexión cerrada")
            return resultados

    except mysql.connector.Error as error:
        print(f"❌ Error al conectar a MySQL: {error}")
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
        return []
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
        return []

def obtener_categorias():
    """
    Obtiene todas las categorías de la tabla tbl_categoria.
    Retorna una lista de diccionarios.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = "SELECT * FROM tbl_categoria ORDER BY id_categoria"
        print(f"🔍 Ejecutando consulta: {query}")
        cursor.execute(query)
        resultados = cursor.fetchall()
        print(f"📦 Categorías obtenidas: {len(resultados)} registros")
        return resultados
        
    except mysql.connector.Error as error:
        print(f"❌ Error al obtener categorías: {error}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al obtener categorías: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def registrar_usuario(nombre, email, password, direccion=None):
    """
    Registra un nuevo usuario en la tabla tbl_usuario.
    
    Args:
        nombre: Nombre del usuario
        email: Email del usuario (debe ser único)
        password: Contraseña del usuario (máximo 10 caracteres según la estructura)
        direccion: Dirección del usuario (opcional)
    
    Returns:
        dict: Diccionario con el resultado de la operación
    """
    conexion = None
    cursor = None
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        # Validar que el email no exista
        cursor.execute("SELECT id_usuario FROM tbl_usuario WHERE email = %s", (email,))
        existe = cursor.fetchone()
        
        if existe:
            return {'success': False, 'message': 'El email ya está registrado'}
        
        # Validar longitud de password
        if len(password) > 10:
            return {'success': False, 'message': 'La contraseña debe tener máximo 10 caracteres'}
        
        # Insertar nuevo usuario
        insert_query = """
            INSERT INTO tbl_usuario (nombre, email, password, direccion, activo, fecha_registro)
            VALUES (%s, %s, %s, %s, TRUE, CURDATE())
        """
        cursor.execute(insert_query, (nombre, email, password, direccion))
        conexion.commit()
        
        # Obtener el ID del usuario recién creado
        cursor.execute("SELECT LAST_INSERT_ID() as id_usuario")
        resultado = cursor.fetchone()
        id_usuario = resultado['id_usuario']
        
        print(f"✅ Usuario registrado exitosamente: ID {id_usuario}")
        return {'success': True, 'message': 'Usuario registrado exitosamente', 'id_usuario': id_usuario}
        
    except mysql.connector.Error as error:
        if conexion:
            conexion.rollback()
        print(f"❌ Error al registrar usuario: {error}")
        return {'success': False, 'message': f'Error en la base de datos: {str(error)}'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"❌ Error inesperado al registrar usuario: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': f'Error inesperado: {str(e)}'}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def ingresar_usuario(email, password):
    """
    Valida las credenciales de un usuario para el ingreso.
    
    Args:
        email: Email del usuario
        password: Contraseña del usuario
    
    Returns:
        dict: Diccionario con el resultado de la validación y datos del usuario si es exitoso
    """
    conexion = None
    cursor = None
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        # Buscar usuario por email y password
        select_query = """
            SELECT id_usuario, nombre, email, direccion, activo, fecha_registro, admin
            FROM tbl_usuario
            WHERE email = %s AND password = %s AND activo = TRUE
        """
        cursor.execute(select_query, (email, password))
        usuario = cursor.fetchone()
        
        if usuario:
            # Verificar si tiene preferencias guardadas
            cursor.execute("SELECT COUNT(*) as count FROM tbl_preferenciafuente WHERE id_usuario = %s", (usuario['id_usuario'],))
            pref_count = cursor.fetchone()['count']
            tiene_preferencias = pref_count > 0
            
            print(f"✅ Ingreso exitoso para usuario: {usuario['email']}. Tiene preferencias: {tiene_preferencias}")
            return {
                'success': True,
                'message': 'Ingreso exitoso',
                'usuario': {
                    'id_usuario': usuario['id_usuario'],
                    'nombre': usuario['nombre'],
                    'email': usuario['email'],
                    'direccion': usuario['direccion'],
                    'admin': usuario['admin'],
                    'tiene_preferencias': tiene_preferencias
                }
            }
        else:
            print(f"❌ Credenciales inválidas para email: {email}")
            return {'success': False, 'message': 'Email o contraseña incorrectos'}
        
    except mysql.connector.Error as error:
        print(f"❌ Error al validar usuario: {error}")
        return {'success': False, 'message': f'Error en la base de datos: {str(error)}'}
    except Exception as e:
        print(f"❌ Error inesperado al validar usuario: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': f'Error inesperado: {str(e)}'}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def guardar_preferencia_defecto(id_usuario):
    """
    Guarda una preferencia de fuente por defecto para el usuario.
    Usado cuando el usuario no configura nada explícitamente.
    También puebla tbl_feed_usuario con las noticias de la fuente por defecto.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # ID Generico = 9 (Según requerimiento)
        id_generico = 9 
        
        # Insertar preferencia por defecto
        # Estructura: id_usuario, id_fuente, prioridad, preferencia_fuente_on_off
        query = """
            INSERT IGNORE INTO tbl_preferenciafuente 
            (id_usuario, id_fuente, prioridad, preferencia_fuente_on_off) 
            VALUES (%s, %s, 1, TRUE)
        """
        cursor.execute(query, (id_usuario, id_generico))
        
        # --- NUEVO: Insertar categoría por defecto ---
        # Variable solicitada
        Id_categoria_generico = 1
        
        # Estructura: id_usuario, id_categoria, orden, preferencia_categoria_on_off
        query_cat = """
            INSERT IGNORE INTO tbl_preferenciacategoria 
            (id_usuario, id_categoria, orden, preferencia_categoria_on_off) 
            VALUES (%s, %s, 1, TRUE)
        """
        cursor.execute(query_cat, (id_usuario, Id_categoria_generico))
        
        # --- NUEVO: Poblar tbl_feed_usuario con noticias de la fuente por defecto ---
        # Insertar todas las noticias de la fuente genérica en el feed del usuario
        query_feed = """
            INSERT IGNORE INTO tbl_feed_usuario (id_usuario, id_noticia, fecha_publicacion, leido)
            SELECT %s, n.id_noticia, n.fecha_hora_publicacion, 0
            FROM tbl_noticia n
            WHERE n.id_fuente = %s
        """
        cursor.execute(query_feed, (id_usuario, id_generico))
        rows_inserted = cursor.rowcount
        
        conexion.commit()
        
        print(f"✅ Preferencia por defecto guardada para usuario {id_usuario} (Fuente ID {id_generico}, Categoria ID {Id_categoria_generico})")
        print(f"✅ Se agregaron {rows_inserted} noticias al feed del usuario")
        return {'success': True, 'message': f'Preferencias por defecto guardadas. {rows_inserted} noticias agregadas al feed.'}
        
    except mysql.connector.Error as error:
        print(f"❌ Error al guardar preferencia defecto: {error}")
        return {'success': False, 'message': str(error)}
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def obtener_categorias_con_preferencias(id_usuario):
    """
    Obtiene todas las categorías junto con la preferencia del usuario especificado.
    Incluye categorías padre y subcategorías.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
        SELECT 
            c.id_categoria,
            c.nombre,
            c.id_categoria_padre,
            -- Si es NULL (no existe registro), lo ponemos en 0 (FALSE)
            COALESCE(pc.preferencia_categoria_on_off, 0) AS esta_suscrito,
            -- Traemos el orden.
            pc.orden
        FROM 
            tbl_categoria c
        -- Hacemos el LEFT JOIN uniendo por categoria Y por el usuario específico
        LEFT JOIN 
            tbl_preferenciacategoria pc 
            ON c.id_categoria = pc.id_categoria AND pc.id_usuario = %s 
        ORDER BY 
            -- Ordenamos por el campo orden (NULLs al final implícitamente o explícitamente si se desea)
            -- MySQL pone NULLs primero por defecto en ASC, así que usaremos un truco si queremos que vayan al final
            -- O simplemente asumimos que si no tiene orden, va al fondo.
            -- Para consistencia con 'suscrito arriba', podemos usar logic similar a fuentes, 
            -- pero el usuario pidió explícitamente 'mediante el campo orden'.
            -- Vamos a priorizar: 1. Orden definido, 2. Nombre
            CASE WHEN pc.orden IS NULL THEN 1 ELSE 0 END, 
            pc.orden ASC,
            c.nombre ASC;
        """
        
        print(f"🔍 Ejecutando consulta de categorías con preferencias para usuario {id_usuario}")
        cursor.execute(query, (id_usuario,))
        resultados = cursor.fetchall()
        print(f"📦 Categorías obtenidas: {len(resultados)} registros")
        return resultados
        
    except mysql.connector.Error as error:
        print(f"❌ Error al obtener categorías con preferencias: {error}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al obtener categorías con preferencias: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def guardar_preferencia_categoria(id_usuario, id_categoria, orden, preferencia_on_off):
    """
    Guarda o actualiza la preferencia de una categoría para un usuario.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        query = """
            INSERT INTO tbl_preferenciacategoria (id_usuario, id_categoria, orden, preferencia_categoria_on_off)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                orden = VALUES(orden),
                preferencia_categoria_on_off = VALUES(preferencia_categoria_on_off)
        """
        
        pref_int = 1 if preferencia_on_off else 0
        
        cursor.execute(query, (id_usuario, id_categoria, orden, pref_int))
        conexion.commit()
        
        print(f"✅ Preferencia categoría guardada: Usuario {id_usuario}, Cat {id_categoria}, Orden {orden}, Estado {pref_int}")
        return {'success': True, 'message': 'Preferencia categoría guardada exitosamente'}
        
    except mysql.connector.Error as error:
        print(f"❌ Error al guardar preferencia categoría: {error}")
        return {'success': False, 'message': str(error)}
    except Exception as e:
        print(f"❌ Error inesperado al guardar preferencia categoría: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

if __name__ == "__main__":
    # Solo para pruebas directas
    print("🔍 Probando conexión a la base de datos...")
    resultados = conectar_base_datos()
    print(f"✅ Resultados obtenidos: {len(resultados)} registros")
    for resultado in resultados:
        print(f"  - {resultado}")

def obtener_fuentes_con_preferencias(id_usuario):
    """
    Obtiene todas las fuentes junto con la preferencia del usuario especificado.
    Si el usuario no tiene preferencia, devuelve NULL (o 0 en esta_suscrito).
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
        SELECT 
            f.id_fuente,
            f.nombre,
            f.url_principal,
            f.avatar_url,
            f.pais,
            -- Creamos una columna virtual: Si es NULL (no existe registro), lo ponemos en 0 (FALSE)
            COALESCE(pf.preferencia_fuente_on_off, 0) AS esta_suscrito,
            -- Traemos la prioridad. Si es NULL, quedará como NULL
            pf.prioridad
        FROM 
            tbl_fuente f
        -- Hacemos el LEFT JOIN uniendo por fuente Y por el usuario específico
        LEFT JOIN 
            tbl_preferenciafuente pf 
            ON f.id_fuente = pf.id_fuente AND pf.id_usuario = %s 
        ORDER BY 
            -- 1. Primero ordenamos por estado: 1 (True) arriba, 0 (False) abajo
            esta_suscrito DESC,
            -- 2. Luego por prioridad (los números más bajos primero: 1, 2, 3...)
            pf.prioridad ASC,
            -- 3. Finalmente, las fuentes no suscritas se ordenan alfabéticamente
            f.nombre ASC;
        """
        
        print(f"🔍 Ejecutando consulta de fuentes con preferencias para usuario {id_usuario}")
        cursor.execute(query, (id_usuario,))
        resultados = cursor.fetchall()
        print(f"📦 Fuentes obtenidas: {len(resultados)} registros")
        return resultados
        
    except mysql.connector.Error as error:
        print(f"❌ Error al obtener fuentes con preferencias: {error}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al obtener fuentes con preferencias: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def guardar_preferencia_fuente(id_usuario, id_fuente, prioridad, preferencia_on_off):
    """
    Guarda o actualiza la preferencia de una fuente para un usuario.
    Usa INSERT ... ON DUPLICATE KEY UPDATE para manejar ambos casos.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # La tabla tiene PK compuesta (id_usuario, id_fuente), así que podemos usar ON DUPLICATE KEY UPDATE
        query = """
            INSERT INTO tbl_preferenciafuente (id_usuario, id_fuente, prioridad, preferencia_fuente_on_off)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                prioridad = VALUES(prioridad),
                preferencia_fuente_on_off = VALUES(preferencia_fuente_on_off)
        """
        
        # Convertir booleano a entero para MySQL (aunque MySQL lo maneja, es más seguro ser explícito)
        pref_int = 1 if preferencia_on_off else 0
        
        cursor.execute(query, (id_usuario, id_fuente, prioridad, pref_int))
        conexion.commit()
        
        print(f"✅ Preferencia guardada: Usuario {id_usuario}, Fuente {id_fuente}, Prioridad {prioridad}, Estado {pref_int}")
        return {'success': True, 'message': 'Preferencia guardada exitosamente'}
        
    except mysql.connector.Error as error:
        print(f"❌ Error al guardar preferencia fuente: {error}")
        return {'success': False, 'message': str(error)}
    except Exception as e:
        print(f"❌ Error inesperado al guardar preferencia fuente: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def actualiza_feed(id_usuario):
    """
    Actualiza el feed del usuario eliminando todas sus entradas actuales
    y reconstruyéndolo basado en sus preferencias de fuentes y categorías.
    
    Args:
        id_usuario: ID del usuario cuyo feed se actualizará
    
    Returns:
        dict: Diccionario con el resultado de la operación
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # 1. Eliminar todas las entradas actuales del feed del usuario
        delete_query = "DELETE FROM tbl_feed_usuario WHERE id_usuario = %s"
        cursor.execute(delete_query, (id_usuario,))
        deleted_count = cursor.rowcount
        print(f"🗑️ Eliminadas {deleted_count} entradas antiguas del feed del usuario {id_usuario}")
        
        # 2. Insertar noticias basadas en las fuentes preferidas (activas)
        query_fuentes = """
            INSERT IGNORE INTO tbl_feed_usuario (id_usuario, id_noticia, fecha_publicacion, leido)
            SELECT DISTINCT %s, n.id_noticia, n.fecha_hora_publicacion, 0
            FROM tbl_noticia n
            INNER JOIN tbl_preferenciafuente pf 
                ON n.id_fuente = pf.id_fuente
            WHERE pf.id_usuario = %s 
                AND pf.preferencia_fuente_on_off = 1
        """
        cursor.execute(query_fuentes, (id_usuario, id_usuario))
        fuentes_count = cursor.rowcount
        print(f"📰 Agregadas {fuentes_count} noticias basadas en fuentes preferidas")
        
        # 3. Insertar noticias basadas en las categorías preferidas (activas)
        query_categorias = """
            INSERT IGNORE INTO tbl_feed_usuario (id_usuario, id_noticia, fecha_publicacion, leido)
            SELECT DISTINCT %s, n.id_noticia, n.fecha_hora_publicacion, 0
            FROM tbl_noticia n
            INNER JOIN tbl_noticia_categoria nc ON n.id_noticia = nc.id_noticia
            INNER JOIN tbl_preferenciacategoria pc 
                ON nc.id_categoria = pc.id_categoria
            WHERE pc.id_usuario = %s 
                AND pc.preferencia_categoria_on_off = 1
        """
        cursor.execute(query_categorias, (id_usuario, id_usuario))
        categorias_count = cursor.rowcount
        print(f"🏷️ Agregadas {categorias_count} noticias basadas en categorías preferidas")
        
        conexion.commit()
        
        total_noticias = fuentes_count + categorias_count
        print(f"✅ Feed actualizado para usuario {id_usuario}: {total_noticias} noticias en total")
        
        return {
            'success': True, 
            'message': f'Feed actualizado exitosamente. {total_noticias} noticias agregadas.',
            'deleted': deleted_count,
            'added': total_noticias
        }
        
    except mysql.connector.Error as error:
        if conexion:
            conexion.rollback()
        print(f"❌ Error al actualizar feed: {error}")
        return {'success': False, 'message': str(error)}
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"❌ Error inesperado al actualizar feed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': str(e)}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def filtra_categoria_feed(id_usuario, id_categoria):
    """
    Filtra el feed del usuario por una categoría específica.

    Args:
        id_usuario: ID del usuario
        id_categoria: ID de la categoría por la que filtrar

    Returns:
        list: Lista de diccionarios con las noticias filtradas
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT f.id_noticia, n.titulo, n.imagen_principal_url, n.cuerpo as resumen,
                   n.fecha_hora_publicacion, fu.nombre as nombre_fuente, n.url_original as url
            FROM tbl_feed_usuario f
            INNER JOIN tbl_noticia n ON f.id_noticia = n.id_noticia
            INNER JOIN tbl_fuente fu ON n.id_fuente = fu.id_fuente
            INNER JOIN tbl_noticia_categoria nc ON n.id_noticia = nc.id_noticia
            WHERE f.id_usuario = %s AND nc.id_categoria = %s
            ORDER BY n.fecha_hora_publicacion DESC
        """

        print(f"🔍 Filtrando feed de usuario {id_usuario} por categoría {id_categoria}")
        cursor.execute(query, (id_usuario, id_categoria))
        noticias = cursor.fetchall()

        # Formatear fechas para JSON
        for n in noticias:
            if n['fecha_hora_publicacion']:
                n['fecha_hora_publicacion'] = n['fecha_hora_publicacion'].strftime('%Y-%m-%d %H:%M:%S')

        print(f"✅ Feed filtrado: {len(noticias)} noticias de categoría {id_categoria}")
        return noticias

    except mysql.connector.Error as error:
        print(f"❌ Error al filtrar feed por categoría: {error}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al filtrar feed por categoría: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

def crear_tabla_preferencia_ubicacion():
    """
    Crea la tabla tbl_preferenciaubicacion si no existe.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        query = """
        CREATE TABLE IF NOT EXISTS tbl_preferenciaubicacion (
            id_preferencia INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            id_ubicacion VARCHAR(50) NOT NULL,
            tipo_ubicacion ENUM('pais', 'region', 'provincia', 'comuna') NOT NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_usuario_ubicacion (id_usuario, id_ubicacion),
            INDEX idx_usuario (id_usuario),
            INDEX idx_tipo (tipo_ubicacion),
            CONSTRAINT fk_pref_ubicacion_usuario 
                FOREIGN KEY (id_usuario) 
                REFERENCES tbl_usuario(id_usuario) 
                ON DELETE CASCADE
        );
        """
        cursor.execute(query)
        conexion.commit()
        print("✅ Tabla tbl_preferenciaubicacion verificada/creada correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al crear tabla tbl_preferenciaubicacion: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

def guardar_preferencias_ubicacion(id_usuario, ubicaciones):
    """
    Guarda las preferencias de ubicación del usuario.
    Primero elimina las existentes y luego inserta las nuevas.
    
    Args:
        id_usuario: ID del usuario
        ubicaciones: Lista de diccionarios [{'id': '...', 'type': '...'}, ...]
    """
    conexion = None
    cursor = None
    try:
        # Asegurar que la tabla exista antes de intentar guardar
        crear_tabla_preferencia_ubicacion()
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # 1. Eliminar preferencias anteriores
        delete_query = "DELETE FROM tbl_preferenciaubicacion WHERE id_usuario = %s"
        cursor.execute(delete_query, (id_usuario,))
        
        # 2. Insertar nuevas preferencias
        if ubicaciones:
            insert_query = """
                INSERT INTO tbl_preferenciaubicacion (id_usuario, id_ubicacion, tipo_ubicacion)
                VALUES (%s, %s, %s)
            """
            values = [(id_usuario, u['id'], u['type']) for u in ubicaciones]
            cursor.executemany(insert_query, values)
            
        conexion.commit()
        count = len(ubicaciones)
        print(f"✅ Guardadas {count} ubicaciones para usuario {id_usuario}")
        return {'success': True, 'message': f'Se guardaron {count} ubicaciones correctamente'}
        
    except mysql.connector.Error as error:
        if conexion: conexion.rollback()
        print(f"❌ Error BD al guardar ubicaciones: {error}")
        return {'success': False, 'message': str(error)}
    except Exception as e:
        if conexion: conexion.rollback()
        print(f"❌ Error inesperado al guardar ubicaciones: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

def obtener_preferencias_ubicacion(id_usuario):
    """
    Obtiene las preferencias de ubicación guardadas para un usuario.
    
    Args:
        id_usuario: ID del usuario
        
    Returns:
        dict: {'success': bool, 'ubicaciones': list}
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
            SELECT id_ubicacion, tipo_ubicacion
            FROM tbl_preferenciaubicacion
            WHERE id_usuario = %s
        """
        cursor.execute(query, (id_usuario,))
        ubicaciones = cursor.fetchall()
        
        print(f"✅ Obtenidas {len(ubicaciones)} ubicaciones para usuario {id_usuario}")
        return {'success': True, 'ubicaciones': ubicaciones}
        
    except mysql.connector.Error as error:
        print(f"❌ Error BD al obtener ubicaciones: {error}")
        return {'success': False, 'ubicaciones': [], 'message': str(error)}
    except Exception as e:
        print(f"❌ Error inesperado al obtener ubicaciones: {e}")
        return {'success': False, 'ubicaciones': [], 'message': str(e)}
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

def obtener_clima_ubicaciones_preferidas(id_usuario, limite=2):
    """
    Obtiene el clima de las primeras N ubicaciones preferidas del usuario.
    
    Args:
        id_usuario: ID del usuario
        limite: Número máximo de ubicaciones a retornar (default: 2)
        
    Returns:
        list: Lista de diccionarios con datos del clima
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        query = """
            SELECT c.id_ubicacion, c.t_actual, c.t_maxima, c.t_minima, c.descripcion, c.icono
            FROM tbl_preferenciaubicacion p
            INNER JOIN tbl_clima c ON CAST(p.id_ubicacion AS CHAR) = CAST(c.id_ubicacion AS CHAR)
            WHERE p.id_usuario = %s
            LIMIT %s
        """
        cursor.execute(query, (id_usuario, limite))
        climas = cursor.fetchall()
        
        print(f"✅ Obtenidos {len(climas)} registros de clima para usuario {id_usuario}")
        return climas
        
    except mysql.connector.Error as error:
        print(f"❌ Error BD al obtener clima: {error}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al obtener clima: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

def rescata_clima(id_usuario):
    """
    Obtiene datos del clima en tiempo real desde la API de Open-Meteo
    para las ubicaciones preferidas del usuario y actualiza tbl_clima.
    
    Args:
        id_usuario: ID del usuario
        
    Returns:
        dict: {'success': bool, 'message': str, 'updated': int}
    """
    conexion = None
    cursor = None
    
    # Mapeo de códigos WMO a descripciones en español
    WMO_CODES = {
        0: ('Despejado', '☀️'),
        1: ('Mayormente despejado', '🌤️'),
        2: ('Parcialmente nublado', '⛅'),
        3: ('Nublado', '☁️'),
        45: ('Neblina', '🌫️'),
        48: ('Neblina con escarcha', '🌫️'),
        51: ('Llovizna ligera', '🌦️'),
        53: ('Llovizna moderada', '🌦️'),
        55: ('Llovizna intensa', '🌧️'),
        61: ('Lluvia ligera', '🌧️'),
        63: ('Lluvia moderada', '🌧️'),
        65: ('Lluvia intensa', '🌧️'),
        71: ('Nieve ligera', '🌨️'),
        73: ('Nieve moderada', '🌨️'),
        75: ('Nieve intensa', '🌨️'),
        77: ('Granizo', '🌨️'),
        80: ('Chubascos ligeros', '🌦️'),
        81: ('Chubascos moderados', '🌧️'),
        82: ('Chubascos intensos', '🌧️'),
        85: ('Chubascos de nieve ligeros', '🌨️'),
        86: ('Chubascos de nieve intensos', '🌨️'),
        95: ('Tormenta', '⛈️'),
        96: ('Tormenta con granizo ligero', '⛈️'),
        99: ('Tormenta con granizo intenso', '⛈️'),
    }
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        # Obtener ubicaciones preferidas del usuario con coordenadas
        query = """
            SELECT DISTINCT p.id_ubicacion, c.latitud, c.longitud
            FROM tbl_preferenciaubicacion p
            LEFT JOIN tbl_clima c ON CAST(p.id_ubicacion AS CHAR) = CAST(c.id_ubicacion AS CHAR)
            WHERE p.id_usuario = %s
            AND c.latitud IS NOT NULL 
            AND c.longitud IS NOT NULL
        """
        cursor.execute(query, (id_usuario,))
        ubicaciones = cursor.fetchall()
        
        if not ubicaciones:
            print(f"⚠️  No se encontraron ubicaciones con coordenadas para usuario {id_usuario}")
            return {
                'success': False, 
                'message': 'No hay ubicaciones con coordenadas configuradas',
                'updated': 0
            }
        
        print(f"🌍 Obteniendo clima para {len(ubicaciones)} ubicaciones...")
        updated_count = 0
        
        for ubicacion in ubicaciones:
            id_ub = ubicacion['id_ubicacion']
            lat = float(ubicacion['latitud'])
            lon = float(ubicacion['longitud'])
            
            try:
                # Llamar a la API de Open-Meteo
                url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    'latitude': lat,
                    'longitude': lon,
                    'current_weather': 'true',
                    'daily': 'temperature_2m_max,temperature_2m_min',
                    'timezone': 'auto',
                    'forecast_days': 1,
                }
                
                print(f"  📡 Consultando clima para {id_ub} ({lat}, {lon})...")
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Extraer datos del clima (Open-Meteo usa 'current_weather')
                current = data.get('current_weather', {})
                t_actual = current.get('temperature')
                weather_code = current.get('weathercode', 0)
                daily = data.get('daily', {})
                # Los valores diarios son listas; tomamos el primer día
                t_maxima = daily.get('temperature_2m_max', [None])[0]
                t_minima = daily.get('temperature_2m_min', [None])[0]
                
                # Obtener descripción e icono del código WMO
                descripcion, icono = WMO_CODES.get(weather_code, ('Desconocido', '❓'))
                
                # Actualizar base de datos
                update_query = """
                    UPDATE tbl_clima 
                    SET t_actual = %s, 
                        t_maxima = %s, 
                        t_minima = %s, 
                        descripcion = %s, 
                        icono = %s,
                        fecha_actualizacion = NOW()
                    WHERE id_ubicacion = %s
                """
                
                cursor.execute(update_query, (
                    t_actual, t_maxima, t_minima, descripcion, icono, id_ub
                ))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    print(f"    ✅ {id_ub}: {t_actual}°C, {descripcion} {icono}")
                
            except requests.exceptions.Timeout:
                print(f"    ⏱️  Timeout al consultar {id_ub}")
            except requests.exceptions.RequestException as e:
                print(f"    ❌ Error de red para {id_ub}: {e}")
            except Exception as e:
                print(f"    ❌ Error procesando {id_ub}: {e}")
        
        conexion.commit()
        
        print(f"\n✅ Clima actualizado: {updated_count}/{len(ubicaciones)} ubicaciones")
        
        return {
            'success': True,
            'message': f'Clima actualizado para {updated_count} ubicaciones',
            'updated': updated_count,
            'total': len(ubicaciones)
        }
        
    except mysql.connector.Error as error:
        if conexion:
            conexion.rollback()
        print(f"❌ Error BD al rescatar clima: {error}")
        return {'success': False, 'message': str(error), 'updated': 0}
    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"❌ Error inesperado al rescatar clima: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': str(e), 'updated': 0}
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()